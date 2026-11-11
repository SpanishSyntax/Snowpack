// ============================================================================
// SNOWPACK DEEP-READER & STUDY COMPANION TEMPLATE (Typst 0.14+)
// Strictly Single-Column Long-Format Textbook & Companion Architecture
// Uses Floe (@local/floe:0.1.0) for Composable Design System & Pedagogical Atoms
// ============================================================================
#import "@local/floe:0.1.0": *

#show: textbook.with(
  title: "__TITLE__",
  subtitle: "__SUBTITLE__",
  course-code: "SC-DEEP",
  institution: "Systems & Control Institute • Academic Series",
  edition: "Comprehensive Companion Edition",
  toc: true,
)

= Executive Foundations

This reader is generated via the *Snowpack Deep-Reader Engine* adhering to the 7-stage pedagogical chapter standard.

#definition(title: "Continuous-Time State Space")[
  An LTI continuous-time system is characterized by the pair of matrix equations:
  $
    dot(x)(t) &= #math-state([A x(t)]) + #math-input([B u(t)]) \
    y(t)       &= #math-sensor([C x(t)]) + #math-noise([D u(t)])
  $
]

#formula-breakdown(
  formula: $dot(x)(t) = A x(t) + B u(t)$,
  ascii: "
   ẋ(t)   =   A · x(t)   +   B · u(t)
    │         │     │        │     │
  State     System State  Actuator Control
 Velocity   Drift Vector  Coupling Input
  ",
  arithmetic: [
    For a 1D scalar system $dot(x) = -2 x + 3 u$ with $x(0) = 1$ and $u = 0$, velocity is $dot(x) = -2$, decaying exponentially.
  ]
)

#data-table(
  columns: (1.2fr, 1.8fr, 1.2fr, 1.5fr),
  headers: ("Problem Class", "Algebraic Form", "Local ⇒ Global?", "Solvers"),
  [Linear Programming], [$min c^T x$ s.t. $A x = b, x >= 0$], [Yes (Vertex)], [Simplex, Interior-Point],
  [Convex QP], [$min 1/2 x^T H x + c^T x$ ($H succ.eq 0$)], [Yes (KKT)], [Schur KKT, Wolfe, Active-Set],
  [Nonlinear Programming], [Smooth non-convex $f, g, h$], [No (Local KKT)], [SQP, Penalty/Barrier],
)
