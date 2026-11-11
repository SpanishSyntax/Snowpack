// ========================================================
// MODULAR TYPST PACKAGE MANIFEST (packages.typ)
// Universal Preamble for Drawing, Notation, Pseudocode & Math
// ========================================================

// --- 1. Vector Drawing & Graphing (The "TikZ" of Typst) ---
#import "@preview/cetz:0.5.2"

// Fletcher provides elegant commutative diagrams, state machines & signal flow
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge

// --- 2. Advanced Mathematics & Physics Notation ---
// Mathematica/Physics notation: differential forms, matrices, bra-kets
#import "@preview/physica:0.9.8": *

// --- 3. Flowcharts & Architecture Diagrams ---
#import "@preview/merman:0.1.0": mermaid

// --- 4. Publication Data Grids & Tables ---
#import "@preview/tablex:0.0.9": tablex, cellx, hlinex, vlinex

// --- 5. Algorithmic Pseudocode ---
#import "@preview/lovelace:0.3.0": *

// --- 6. Engineering SI Units & Formatting ---
#import "@preview/unify:0.7.0": *

// ========================================================
// Q2 PROFESSOR-STYLE SEMANTIC EQUATION PALETTE
// ========================================================
#let c-state   = rgb("#0284C7")  // Sky Blue: State variables x, internal drift Ax, primal objective f(x)
#let c-input   = rgb("#DC2626")  // Crimson Red: Control input u, actuator matrix B, inequality g(x)
#let c-cost    = rgb("#D97706")  // Amber: Cost weights Q/R, Lagrange multipliers \lambda, slack
#let c-sensor  = rgb("#059669")  // Emerald Green: Measurements y, sensors C, reference target r(t)
#let c-noise   = rgb("#7C3AED")  // Royal Purple: Disturbance w, sensor noise v, equality h(x), dual \mu
#let c-est     = rgb("#DB2777")  // Deep Pink: Estimated states \hat{x}, residuals, bounds

#let math-state(x)   = text(fill: c-state, weight: "bold")[$#x$]
#let math-input(x)   = text(fill: c-input, weight: "bold")[$#x$]
#let math-cost(x)    = text(fill: c-cost, weight: "bold")[$#x$]
#let math-sensor(x)  = text(fill: c-sensor, weight: "bold")[$#x$]
#let math-noise(x)   = text(fill: c-noise, weight: "bold")[$#x$]
#let math-est(x)     = text(fill: c-est, weight: "bold")[$#x$]

#let math-annot(term, label, color: c-state) = {
  $underbrace(#text(fill: color)[$#term$], #text(fill: color, size: 7.5pt, font: "Liberation Sans")[#label])$
}
#let math-annot-top(term, label, color: c-state) = {
  $overbrace(#text(fill: color)[$#term$], #text(fill: color, size: 7.5pt, font: "Liberation Sans")[#label])$
}

// ========================================================
// STANDARD SYSTEMS & CONTROL MATHEMATICAL OPERATORS
// ========================================================
#let argmin   = math.op("arg min", limits: true)
#let argmax   = math.op("arg max", limits: true)
#let diag     = math.op("diag")
#let rank     = math.op("rank")
#let tr       = math.op("tr")
#let sign     = math.op("sign")
#let span-op  = math.op("span")
#let col      = math.op("col")
#let null-op  = math.op("null")
#let ker      = math.op("ker")
#let im-op    = math.op("im")
#let Re       = math.op("Re")
#let Im       = math.op("Im")
#let ddot(x)  = math.dot.double(x)
#let st       = $quad "s.t." quad$
#let Rn       = $RR^n$
#let Rm       = $RR^m$
#let Rp       = $RR^p$
#let Rnxn     = $RR^(n times n)$
#let Rnxm     = $RR^(n times m)$
#let Rpxn     = $RR^(p times n)$
#let Rpxm     = $RR^(p times m)$
