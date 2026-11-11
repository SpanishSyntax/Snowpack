// ============================================================================
// SNOWPACK EXECUTIVE DECISION MEMO (Typst 0.14+)
// Powered by Floe Design System (@local/floe:0.1.0)
// ============================================================================
#import "@local/floe:0.1.0": *

#show: memo.with(
  title: "__TITLE__",
  to: "Systems & Control Board",
  from: "__AUTHOR__",
  date: "__DATE__",
  subject: "__SUBTITLE__",
  summary: [
    Executive decision brief generated via the *Snowpack Engine* using the *Floe Design System*.
  ],
)

= Problem Statement

#warning-box(title: "Critical Operational Bottleneck")[
  System latency currently exceeds SLA thresholds under peak loads.
]

= Proposed Architecture & Tradeoffs

#pro-con(
  pros: (
    [Sub-millisecond deterministic evaluation],
    [Zero runtime memory allocations in control loop],
  ),
  cons: (
    [Increased ahead-of-time compilation footprint],
  ),
)
