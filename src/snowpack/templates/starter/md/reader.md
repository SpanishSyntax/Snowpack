---
title: "__TITLE__"
subtitle: "__SUBTITLE__"
author: "__AUTHOR__"
dependency: "Delft Center for Systems and Control (DCSC)"
date: "__DATE__"
mode: "report"
preset: "reader"
engine: "__ENGINE__"
---

# Foundations & Course Scope

This document is authored using the **Snowpack Deep-Reader Markdown Specification**.

## Physical Mechanical Anchor

In mechatronic and aerospace systems, physical constraints dictate actuator saturation and energy dissipation.

## Mathematical Formulation

Consider the state-space dynamic model characterized by:

$$\dot{\mathbf{x}}(t) = \mathbf{A}\mathbf{x}(t) + \mathbf{B}\mathbf{u}(t)$$

Under stabilizability conditions, there exists a state-feedback gain $\mathbf{K}$ such that the closed-loop eigenvalues of $(\mathbf{A} - \mathbf{B}\mathbf{K})$ lie strictly in the left half of the complex plane $\mathbb{C}^-$.

## Algorithm Implementation

```python
def lqr_gain(A, B, Q, R):
    """Computes continuous-time LQR optimal gain via Riccati equation."""
    import scipy.linalg
    P = scipy.linalg.solve_continuous_are(A, B, Q, R)
    return scipy.linalg.inv(R) @ B.T @ P
```
