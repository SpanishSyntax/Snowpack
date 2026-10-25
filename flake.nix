{
  description = "Snowpack - Markdown to Beautiful Typst PDF Document Compiler";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    prism = {
      url = "git+ssh://git@github.com/SpanishSyntax/Prism.git";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    prism,
  }: let
    systems = flake-utils.lib.defaultSystems;
  in
    flake-utils.lib.eachSystem systems (system: let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [prism.overlays.default];
      };
      lib = pkgs.lib;

      snowpackPackage = pkgs.python3Packages.buildPythonApplication {
        pname = "snowpack";
        version = "0.1.0";
        src = ./.;
        pyproject = true;

        build-system = [
          pkgs.python3Packages.setuptools
        ];

        propagatedBuildInputs = [
          pkgs.python3Packages.prism
        ];

        nativeBuildInputs = [
          pkgs.makeWrapper
        ];

        postFixup = ''
          wrapProgram $out/bin/snowpack \
            --prefix PATH : ${lib.makeBinPath [pkgs.pandoc pkgs.typst pkgs.tectonic]}
        '';

        nativeCheckInputs = [
          pkgs.python3Packages.pytest
        ];

        doCheck = false;

        meta = with lib; {
          description = "Markdown to Typst & LaTeX Multi-Mode Document Compiler";
          homepage = "https://github.com/SpanishSyntax/Snowpack";
          license = licenses.mit;
          mainProgram = "snowpack";
        };
      };
    in {
      packages = {
        default = snowpackPackage;
        snowpack = snowpackPackage;
      };

      apps = {
        default = {
          type = "app";
          program = "${snowpackPackage}/bin/snowpack";
        };
        snowpack = {
          type = "app";
          program = "${snowpackPackage}/bin/snowpack";
        };
      };

      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          python3
          python3Packages.setuptools
          python3Packages.pytest
          python3Packages.prism
          pandoc
          typst
          tectonic
        ];
      };
    })
    // {
      overlays = {
        default = final: prev: {
          snowpack = self.packages.${prev.stdenv.hostPlatform.system}.default;
        };
        snowpack = self.overlays.default;
      };

      nixosModules = {
        default = self.nixosModules.snowpack;
        snowpack = {
          config,
          lib,
          pkgs,
          ...
        }: let
          cfg = config.programs.snowpack;
          system = pkgs.stdenv.hostPlatform.system;
          defaultSnowpack = self.packages.${system}.default;
        in {
          options.programs.snowpack = {
            enable = lib.mkEnableOption "Snowpack - Markdown to Typst PDF Document Compiler";

            package = lib.mkOption {
              type = lib.types.package;
              default = defaultSnowpack;
              description = "The Snowpack package to use.";
            };
          };

          config = lib.mkIf cfg.enable {
            environment.systemPackages = [cfg.package];
          };
        };
      };

      homeManagerModules = {
        default = self.homeManagerModules.snowpack;
        snowpack = {
          config,
          lib,
          pkgs,
          ...
        }: let
          cfg = config.programs.snowpack;
          tomlFormat = pkgs.formats.toml {};
          system = pkgs.stdenv.hostPlatform.system;
          defaultSnowpack = self.packages.${system}.default;
        in {
          options.programs.snowpack = {
            enable = lib.mkEnableOption "Snowpack - Markdown to Typst PDF Document Compiler";

            package = lib.mkOption {
              type = lib.types.package;
              default = defaultSnowpack;
              description = "The Snowpack package to use.";
            };

            settings = lib.mkOption {
              type = tomlFormat.type;
              default = {};
              description = "Configuration written to ~/.config/snowpack/snowpack.toml.";
            };
          };

          config = lib.mkIf cfg.enable {
            home.packages = [cfg.package];

            xdg.configFile."snowpack/snowpack.toml" = lib.mkIf (cfg.settings != {}) {
              source = tomlFormat.generate "snowpack.toml" cfg.settings;
            };
          };
        };
      };
    };
}
