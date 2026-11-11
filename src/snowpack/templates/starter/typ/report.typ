// ========================================================
// SNOWPACK MINIMAL SANS-SERIF REPORT TEMPLATE (Typst 0.13+)
// ========================================================
#import "@preview/mmdr:0.2.2": mermaid
#import "/packages.typ": *

// ==========================================
// COLOR PALETTE
// ==========================================
#let theme = (
  text: rgb("#18181b"),
  heading: rgb("#09090b"),
  grey-900: rgb("#18181b"),
  grey-800: rgb("#27272a"),
  grey-700: rgb("#3f3f46"),
  grey-600: rgb("#52525b"),
  grey-500: rgb("#71717a"),
  grey-400: rgb("#a1a1aa"),
  grey-300: rgb("#d4d4d8"),
  grey-200: rgb("#e4e4e7"),
  grey-100: rgb("#f4f4f5"),
  subtle-text: rgb("#3f3f46"),
  muted: rgb("#71717a"),
  border: rgb("#e4e4e7"),
  border-dark: rgb("#27272a"),
  bg-subtle: rgb("#f4f4f5"),
  highlight: rgb("#fef08a"),
  inserted: rgb("#15803d"),
)

// ==========================================
// GLOBAL FONT FAMILIES
// ==========================================
#let fonts = (
  sans: ("Inter", "Liberation Sans", "FreeSans"),
  display: ("Inter Display", "Inter"),
  mono: ("Iosevka NF", "Source Code Pro", "Consolas"),
)

#let horizontalrule = (
  v(0.5em) + line(length: 100%, stroke: 0.35pt + theme.border) + v(0.5em)
)

// ==========================================
// Q2 PROFESSOR-STYLE EQUATION COLOR PALETTE & HELPERS
// ==========================================
#let c-state   = rgb("#0284C7")  // Sky Blue: Internal dynamics, state x, autonomous drift
#let c-input   = rgb("#DC2626")  // Crimson Red: Actuator authority, control input u, constraints
#let c-cost    = rgb("#D97706")  // Amber: Cost weights Q/R, Lagrange multipliers \lambda
#let c-sensor  = rgb("#059669")  // Emerald Green: Measurements y, sensors, reference target
#let c-noise   = rgb("#7C3AED")  // Royal Purple: Disturbance w, sensor noise v, duals \mu
#let c-est     = rgb("#DB2777")  // Deep Pink: Estimated states \hat{x}, residuals, bounds

#let math-state(x)   = text(fill: c-state, weight: "bold")[$#x$]
#let math-input(x)   = text(fill: c-input, weight: "bold")[$#x$]
#let math-cost(x)    = text(fill: c-cost, weight: "bold")[$#x$]
#let math-sensor(x)  = text(fill: c-sensor, weight: "bold")[$#x$]
#let math-noise(x)   = text(fill: c-noise, weight: "bold")[$#x$]
#let math-est(x)     = text(fill: c-est, weight: "bold")[$#x$]

#let math-annot(term, label, color: c-state) = {
  $underbrace(#text(fill: color)[$#term$], #text(fill: color, size: 7.5pt, font: fonts.sans)[#label])$
}
#let math-annot-top(term, label, color: c-state) = {
  $overbrace(#text(fill: color)[$#term$], #text(fill: color, size: 7.5pt, font: fonts.sans)[#label])$
}

#let eq-legend(..items) = {
  block(
    width: 100%,
    fill: rgb("#F8FAFC"),
    stroke: 0.5pt + rgb("#CBD5E1"),
    radius: 3pt,
    inset: (x: 10pt, y: 7pt),
    above: 0.6em,
    below: 1.0em,
  )[
    #set text(font: fonts.sans, size: 8.3pt)
    #grid(
      columns: (auto, 1fr),
      gutter: 8pt,
      ..items.pos().map(it => (
        [#box(width: 8pt, height: 8pt, fill: it.at(0), radius: 2pt)],
        [*#it.at(1):* #h(4pt) #it.at(2)]
      )).flatten()
    )
  ]
}

// ==========================================
// DAVID C. LAY "NOTICE ME" DEFINITION & THEOREM BLOCKS
// ==========================================
#let definition(title: none, term: none, intuition: none, body) = block(
  width: 100%,
  breakable: true,
  stroke: (left: 4.5pt + c-state, rest: 0.75pt + rgb("#CBD5E1")),
  radius: (right: 4pt),
  fill: rgb("#F8FAFC"),
  above: 1.25em,
  below: 1.25em,
)[
  #block(
    width: 100%,
    fill: rgb("#0C2340"),
    inset: (x: 12pt, y: 6.5pt),
  )[
    #grid(
      columns: (auto, 1fr),
      gutter: 8pt,
      align: (left + horizon, right + horizon),
      [
        #box(
          fill: c-state,
          inset: (x: 5pt, y: 2.5pt),
          radius: 2pt,
          text(font: fonts.sans, size: 8pt, weight: "bold", fill: white, tracking: 0.08em)[DEFINITION]
        )
        #if term != none [
          #h(8pt)
          #text(font: fonts.sans, size: 9.5pt, weight: "bold", fill: white)[#term]
        ]
      ],
      [
        #if title != none [
          #text(font: fonts.sans, size: 8.5pt, weight: "bold", fill: rgb("#94A3B8"))[#title]
        ]
      ]
    )
  ]
  #block(
    width: 100%,
    inset: (x: 13pt, top: 10pt, bottom: if intuition != none { 6pt } else { 10pt }),
  )[
    #set par(justify: true)
    #body
  ]
  #if intuition != none [
    #block(
      width: 100%,
      fill: rgb("#EFF6FF"),
      stroke: (top: 0.5pt + rgb("#BFDBFE")),
      inset: (x: 13pt, y: 6pt),
    )[
      #set text(font: fonts.sans, size: 8.5pt, fill: rgb("#1E40AF"))
      *Geometric / Physical Intuition:* #h(4pt) #intuition
    ]
  ]
]

#let theorem(title: none, name: none, takeaway: none, body) = block(
  width: 100%,
  breakable: true,
  stroke: (left: 4.5pt + rgb("#0C2340"), rest: 0.75pt + rgb("#CBD5E1")),
  radius: (right: 4pt),
  fill: rgb("#FFFFFF"),
  above: 1.25em,
  below: 1.25em,
)[
  #block(
    width: 100%,
    fill: rgb("#0C2340"),
    inset: (x: 12pt, y: 6.5pt),
  )[
    #grid(
      columns: (auto, 1fr),
      gutter: 8pt,
      align: (left + horizon, right + horizon),
      [
        #box(
          fill: c-cost,
          inset: (x: 5pt, y: 2.5pt),
          radius: 2pt,
          text(font: fonts.sans, size: 8pt, weight: "bold", fill: white, tracking: 0.08em)[THEOREM]
        )
        #if name != none [
          #h(8pt)
          #text(font: fonts.sans, size: 9.5pt, weight: "bold", fill: white)[#name]
        ]
      ],
      [
        #if title != none [
          #text(font: fonts.sans, size: 8.5pt, weight: "bold", fill: rgb("#94A3B8"))[#title]
        ]
      ]
    )
  ]
  #block(
    width: 100%,
    inset: (x: 13pt, top: 10pt, bottom: if takeaway != none { 6pt } else { 10pt }),
  )[
    #set par(justify: true)
    #body
  ]
  #if takeaway != none [
    #block(
      width: 100%,
      fill: rgb("#FFFBEB"),
      stroke: (top: 0.5pt + rgb("#FDE68A")),
      inset: (x: 13pt, y: 6pt),
    )[
      #set text(font: fonts.sans, size: 8.5pt, fill: rgb("#92400E"))
      *Key Engineering Takeaway:* #h(4pt) #takeaway
    ]
  ]
]

#let formula-breakdown(formula: none, ascii: "", arithmetic: none) = block(
  width: 100%,
  stroke: 1pt + rgb("#CBD5E1"),
  radius: 4pt,
  fill: rgb("#FBFBFE"),
  inset: 10pt,
  above: 1.1em,
  below: 1.3em,
)[
  #block(below: 6pt)[
    #box(fill: rgb("#334155"), inset: (x: 5pt, y: 2pt), radius: 2pt)[
      #text(font: fonts.sans, size: 7.5pt, weight: "bold", fill: white, tracking: 0.08em)[FORMULA BREAKDOWN]
    ]
    #h(6pt)
    #text(font: fonts.sans, size: 8.5pt, weight: "bold", fill: rgb("#0C2340"))[Symbol-by-Symbol Mechanics]
  ]
  #if formula != none [
    #align(center)[#block(fill: white, inset: (x: 12pt, y: 6pt), stroke: 0.5pt + rgb("#E2E8F0"), radius: 3pt)[
      #text(size: 11pt)[$#formula$]
    ]]
    #v(3pt)
  ]
  #align(center)[
    #raw(ascii, lang: "text")
  ]
  #if arithmetic != none [
    #v(4pt)
    #line(length: 100%, stroke: 0.35pt + rgb("#E2E8F0"))
    #v(4pt)
    #text(font: fonts.sans, size: 8.5pt, weight: "bold", fill: c-sensor)[Concrete Numerical Verification:]
    #h(6pt)
    #arithmetic
  ]
]
#let cutting-board = formula-breakdown

#let report(
  title: none,
  subtitle: none,
  author: "Author",
  dependency: none,
  date: datetime.today().display("[Day]/[Month repr:numerical]/[Year]"),
  doc,
  ..sink,
) = {
  let front-title = title
  let final-subtitle = subtitle
  let final-author = author
  let final-dep = dependency
  let final-date = date

  // ==========================================
  // PAGE CONFIGURATION
  // ==========================================
  set page(
    paper: "a4",
    margin: (
      x: 2.2cm,
      top: 2.5cm,
      bottom: 2.5cm,
    ),
    header: context {
      set text(
        font: fonts.sans,
        size: 8pt,
        fill: theme.muted,
      )

      if here().page() > 1 {
        grid(
          columns: (1fr, 1fr),
          align(left)[#if final-author != none [#upper(final-author)]],
          align(right)[#final-date],
        )

        v(4pt)

        line(
          length: 100%,
          stroke: 0.35pt + theme.border,
        )
      }
    },
    footer: context {
      set text(
        font: fonts.sans,
        size: 8pt,
        fill: theme.muted,
      )

      line(
        length: 100%,
        stroke: 0.35pt + theme.border,
      )

      v(6pt)

      grid(
        columns: (1fr, 1fr),
        align(left)[
          #if final-dep != none [#final-dep #h(4pt) — #h(4pt)]
          #if final-author != none [#final-author]
        ],
        align(right)[
          Page
          #counter(page).display()
          of
          #counter(page).final().first()
        ],
      )
    },
  )

  // ==========================================
  // BASE TYPOGRAPHY
  // ==========================================
  set text(
    font: fonts.sans,
    size: 9.5pt,
    fill: theme.text,
    lang: "en",
    region: "us"
  )

  set par(
    justify: true,
    leading: 0.65em,
    spacing: 1.5em,
    first-line-indent: 1em,
  )

  // ==========================================
  // TITLE BANNER (Only if provided in frontmatter)
  // ==========================================
  if front-title != none {
    block(
      width: 100%,
      inset: (bottom: 12pt),
    )[
      #text(
        size: 24pt,
        weight: "bold",
        fill: theme.heading,
        tracking: -0.025em,
      )[
        #front-title
      ]

      #if final-subtitle != none [
        #v(3pt)
        #text(
          size: 11.5pt,
          weight: "regular",
          fill: theme.muted,
        )[
          #final-subtitle
        ]
      ]

      #if final-author != none or final-dep != none [
        #v(5pt)
        #grid(
          columns: (1fr, 1fr),
          gutter: 12pt,
          if final-author != none [
            #text(
              size: 7.5pt,
              fill: theme.muted,
              tracking: 0.05em,
            )[AUTHOR]

            #v(2pt)

            #text(
              size: 8.5pt,
              weight: "bold",
              fill: theme.heading,
            )[#final-author]
          ],
          if final-dep != none [
            #text(
              size: 7.5pt,
              fill: theme.muted,
              tracking: 0.05em,
            )[DEPENDENCY]

            #v(2pt)

            #text(
              size: 8.5pt,
              weight: "bold",
              fill: theme.heading,
            )[#final-dep]
          ],
        )
      ]
    ]
    v(0.35em)
  }

  // ==========================================
  // TYPOGRAPHIC HIERARCHY
  // ==========================================
  show heading: set block(
    above: 1.4em,
    below: 0.8em,
  )

  show heading.where(level: 1): it => block(
    above: 1.8em,
    below: 1.0em,
    text(
      size: 22pt,
      weight: "bold",
      fill: theme.heading,
      tracking: -0.035em,
      it.body,
    ),
  )

  show heading.where(level: 2): it => block(
    above: 1.5em,
    below: 1em,
    text(
      size: 15pt,
      weight: "bold",
      fill: theme.grey-800,
      tracking: -0.02em,
      it.body,
    ),
  )

  show heading.where(level: 3): it => block(
    above: 1.4em,
    below: 1em,
    text(
      size: 11.5pt,
      weight: "bold",
      fill: theme.grey-500,
      tracking: -0.005em,
      it.body,
    ),
  )

  show heading.where(level: 4): it => block(
    above: 1.3em,
    below: 1em,
    text(
      size: 8.5pt,
      weight: "bold",
      style: "italic",
      fill: theme.grey-800,
      tracking: 0.14em,
      upper(it.body),
    ),
  )

  show heading.where(level: 5): it => block(
    above: 1.2em,
    below: 1em,
    text(
      size: 9.5pt,
      weight: "light",
      style: "italic",
      fill: theme.grey-600,
      it.body,
    ),
  )

  show heading.where(level: 6): it => block(
    above: 1.2em,
    below: 1em,
    text(
      size: 8pt,
      weight: "bold",
      style: "oblique",
      fill: theme.grey-600,
      it.body,
    ),
  )

  // ==========================================
  // BLOCKQUOTES
  // ==========================================
  show quote.where(block: true): it => {
    pad(
      left: 0.5em,
      y: 0.35em,
    )[
      #block(
        stroke: (
          left: 1.5pt + theme.grey-800,
        ),
        inset: (
          left: 10pt,
          y: 2pt,
        ),
        text(
          fill: theme.subtle-text,
          style: "normal",
          it.body,
        ),
      )
    ]
  }

  // ==========================================
  // CODE BLOCKS
  // ==========================================
  show raw.where(block: true): it => {
    block(
      width: 100%,
      fill: theme.bg-subtle,
      inset: (
        x: 12pt,
        y: 10pt,
      ),
      radius: 4pt,
      stroke: 0.3pt + theme.border,
      text(
        font: fonts.mono,
        size: 8pt,
        fill: theme.text,
        it,
      ),
    )
  }

  // ==========================================
  // INLINE CODE
  // ==========================================
  show raw.where(block: false): it => {
    box(
      fill: theme.bg-subtle,
      inset: (
        x: 4pt,
        y: 1.5pt,
      ),
      radius: 3pt,
      stroke: 0.3pt + theme.border,
      text(
        font: fonts.mono,
        size: 8pt,
        fill: theme.heading,
        it,
      ),
    )
  }

  // ==========================================
  // TABLES
  // ==========================================
  set table(
    stroke: none,
    inset: (
      x: 8pt,
      y: 7pt,
    ),
  )

  show table.cell: it => {
    set text(
      size: 8.5pt,
    )
    it
  }

  show table.cell.where(y: 0): it => {
    set text(
      weight: "bold",
      fill: theme.heading,
    )
    it
  }

  show table: it => block(
    stroke: (
      top: 0.5pt + theme.grey-800,
      bottom: 0.5pt + theme.grey-800,
    ),
    it,
  )

  // ==========================================
  // MERMAID
  // ==========================================
  show raw.where(lang: "mermaid"): it => {
    align(
      center,
      mermaid(it.text),
    )
  }

  // ==========================================
  // HTML <mark>
  // ==========================================
  show <mark>: it => box(
    fill: theme.highlight,
    inset: (
      x: 3pt,
      y: 1pt,
    ),
    outset: (
      y: 1.5pt,
    ),
    radius: 2pt,
    it,
  )

  // ==========================================
  // HTML <ins>
  // ==========================================
  show <ins>: it => text(
    fill: theme.inserted,
  )[
    #underline(
      offset: 2pt,
    )[
      #it
    ]
  ]

  doc
}

#show: report.with(
  title: [__TITLE__],
  subtitle: [__SUBTITLE__],
  author: "__AUTHOR__",
  dependency: "__DEPENDENCY__",
  date: "__DATE__",
)

This document uses strictly native Typst markup and imports modular packages from `/packages.typ`.

= Executive Summary

Modern engineering systems demand rigorous specification, reproducible documentation, and verified analytical models. This report outlines the operational envelope, hardware-in-the-loop verification, and dynamic state-space models.

= Mathematical Formulation

Consider the state-space dynamic model characterized by:

$
  dot(bold(x))(t) &= bold(A) bold(x)(t) + bold(B) bold(u)(t) \
  bold(y)(t)       &= bold(C) bold(x)(t) + bold(D) bold(u)(t)
$

Under stabilizability conditions, there exists a state-feedback gain $bold(K)$ such that the closed-loop eigenvalues of $(bold(A) - bold(B) bold(K))$ lie strictly in the left half of the complex plane $CC^-$.

= Subsystem Benchmarks

Performance across distributed nodes was validated against official benchmarks.

#align(center)[
  #table(
    columns: (auto, 1.5fr, 1fr, auto),
    inset: 9pt,
    align: (col, row) => if row == 0 { center + horizon } else { left + horizon },
    stroke: (x, y) => if y == 0 { (bottom: 1.5pt + black) } else { (bottom: 0.5pt + gray) },
    [*Node ID*], [*Component Name*], [*Status*], [*Throughput*],
    [*NODE-01*], [Ingestion Pipeline], [`Nominal`], [420.5 MB/s],
    [*NODE-02*], [Consensus Engine], [`Nominal`], [180.2 MB/s],
    [*NODE-03*], [Matrix Solver Core], [`Optimal`], [950.0 MB/s],
  )
]

= Algorithm Implementation

```python
def update_state(x, u, dt=0.01):
    """Computes single-step state propagation."""
    return x + (A @ x + B @ u) * dt
```

= Conclusions

The architecture satisfies all real-time requirements with zero dynamic memory allocations in the inner loop.

#bibliography("/library.bib", title: "References")
