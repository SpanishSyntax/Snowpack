// ============================================================================
// SNOWPACK EXECUTIVE BRIEF & DECISION MEMO TEMPLATE (Typst 0.14+)
// High-Impact Strategic Technical Memorandum & Project Review
// ============================================================================
#import "/packages.typ": *

#let floe-cyan   = rgb("#00A6D6")
#let floe-navy   = rgb("#0C2340")
#let floe-slate  = rgb("#334155")
#let floe-muted  = rgb("#64748B")
#let floe-green  = rgb("#059669")
#let floe-amber  = rgb("#B45309")
#let floe-red    = rgb("#DC2626")

#let exec-doc(
  title: "__TITLE__",
  subtitle: "__SUBTITLE__",
  author: "__AUTHOR__",
  target-audience: "Steering Committee / Technical Leadership",
  date: "__DATE__",
  status: "FOR DECISION",
  body,
) = {
  set document(title: title, author: author)
  set page(
    paper: "a4",
    margin: (x: 2.2cm, top: 2.2cm, bottom: 2.2cm),
    header: context {
      if here().page() > 1 {
        set text(font: "Liberation Sans", size: 8.5pt, fill: floe-slate)
        grid(
          columns: (1fr, 1fr),
          align(left)[#smallcaps(title)],
          align(right)[#here().page()],
        )
        v(3pt)
        line(length: 100%, stroke: 0.35pt + rgb("#CBD5E1"))
      }
    },
  )
  set text(font: "Liberation Sans", size: 9.8pt, fill: rgb("#0F172A"))
  set par(justify: true, leading: 0.6em)

  // Header Banner
  block(width: 100%, below: 1.2em)[
    #grid(
      columns: (1fr, auto),
      gutter: 12pt,
      align: (left + horizon, right + horizon),
      [
        #text(size: 8pt, weight: "bold", fill: floe-cyan, tracking: 0.12em)[EXECUTIVE MEMORANDUM]
        #v(2pt)
        #text(size: 18pt, weight: "bold", fill: floe-navy)[#title]
        #if subtitle != "" [
          #v(1pt)
          #text(size: 11pt, fill: floe-slate)[#subtitle]
        ]
      ],
      [
        #box(
          fill: if status == "FOR DECISION" { rgb("#EFF6FF") } else { rgb("#F8FAFC") },
          stroke: 1pt + if status == "FOR DECISION" { floe-cyan } else { rgb("#CBD5E1") },
          inset: (x: 10pt, y: 5pt),
          radius: 3pt,
          align(center)[
            #text(size: 8pt, weight: "bold", fill: if status == "FOR DECISION" { floe-cyan } else { floe-slate })[#status]
          ]
        )
      ]
    ]
    #v(6pt)
    #line(length: 100%, stroke: 1.5pt + floe-cyan)
    #v(4pt)
    #grid(
      columns: (1fr, 1fr, 1fr),
      gutter: 8pt,
      [#text(size: 8pt, fill: floe-muted)[*AUTHOR:*] #h(4pt) #text(size: 8.5pt)[#author]],
      [#text(size: 8pt, fill: floe-muted)[*DATE:*] #h(4pt) #text(size: 8.5pt)[#date]],
      [#text(size: 8pt, fill: floe-muted)[*AUDIENCE:*] #h(4pt) #text(size: 8.5pt)[#target-audience]],
    )
    #v(2pt)
    #line(length: 100%, stroke: 0.35pt + rgb("#E2E8F0"))
  ]

  body
}

#let kpi-card(label, value, delta: none, positive: true) = block(
  fill: rgb("#F8FAFC"),
  stroke: 0.5pt + rgb("#E2E8F0"),
  radius: 4pt,
  inset: (x: 10pt, y: 8pt),
)[
  #text(size: 8pt, fill: floe-muted, weight: "bold")[#upper(label)]
  #v(2pt)
  #text(size: 15pt, weight: "bold", fill: floe-navy)[#value]
  #if delta != none [
    #h(6pt)
    #text(
      size: 8.5pt,
      weight: "bold",
      fill: if positive { floe-green } else { floe-red },
    )[#delta]
  ]
]

#let decision-callout(title: "Strategic Recommendation", body) = block(
  width: 100%,
  stroke: (left: 4.5pt + floe-cyan, rest: 0.5pt + rgb("#BAE6FD")),
  fill: rgb("#F0F9FF"),
  radius: (right: 4pt),
  inset: 12pt,
  above: 1.2em,
  below: 1.2em,
)[
  #text(size: 9pt, weight: "bold", fill: floe-cyan, tracking: 0.05em)[ACTION REQUIRED]
  #h(6pt)
  #text(size: 10pt, weight: "bold", fill: floe-navy)[— #title]
  #v(4pt)
  #set par(justify: true)
  #body
]

#show: exec-doc.with(
  title: "__TITLE__",
  subtitle: "__SUBTITLE__",
  author: "__AUTHOR__",
)

#decision-callout(title: "Executive Synthesis & Core Decision")[
  This executive brief outlines the critical architecture choices, system trade-offs, and deployment timeline. Immediate approval is requested to lock the target specifications.
]

= Performance & Operational Metrics

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 10pt,
  kpi-card("Latency Ceiling", "< 12 ms", delta: "-40%", positive: true),
  kpi-card("State Estimation Error", "0.042 rad", delta: "-18%", positive: true),
  kpi-card("Actuator Headroom", "28.5%", delta: "+12%", positive: true),
)

= Key Decisions & Comparative Trade-Offs

#table(
  columns: (1.5fr, 2fr, 2fr, 1fr),
  fill: (col, row) => if row == 0 { rgb("#0C2340") } else if calc.even(row) { rgb("#F8FAFC") } else { white },
  stroke: (col, row) => 0.4pt + rgb("#CBD5E1"),
  inset: 7pt,
  align: (col, row) => if row == 0 { center + horizon } else { left + horizon },
  table.header(
    [*Architecture Vector*],
    [*Option A (Baseline)*],
    [*Option B (Selected)*],
    [*Status*],
  ),
  [State Estimator], [Standard Discrete Kalman Filter], [Square-Root Unscented Kalman Filter], [Approved],
  [Optimization Solver], [Interior-Point (Primal-Dual)], [Operator-Splitting QP (OSQP)], [Approved],
  [Compute Platform], [ARM Cortex-M7 @ 480MHz], [Heterogeneous Cortex-A53 + FPGA], [Proposed],
)

= Risk Mitigation & Deployment Timeline

- *Milestone M1 (Week 2):* Complete software-in-the-loop (SIL) validation across edge perturbation envelope.
- *Milestone M2 (Week 4):* Real-time hardware-in-the-loop (HIL) bench verification.
- *Milestone M3 (Week 6):* Sign-off and flight test operational deployment.
