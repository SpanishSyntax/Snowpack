// ============================================================================
// SNOWPACK CLOSED-BOOK EXAM CHEATSHEET (Typst 0.14+)
// High-Density Multi-Column Reference Powered by Floe (@local/floe:0.1.0)
// ============================================================================
#import "@local/floe:0.1.0": *

#show: cheatsheet.with(
  title: "__TITLE__",
  course-code: "__SUBTITLE__",
  columns-num: 3,
)

= State Space & Dynamics

#definition(title: "Continuous-Time LTI System")[
  $dot(x)(t) = A x(t) + B u(t)$, $y(t) = C x(t) + D u(t)$
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
    Asymptotically stable iff all eigenvalues of $A$ have strictly negative real parts: $Re(lambda_i(A)) < 0$.
  ]
)
