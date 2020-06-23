---
title: Quantum Optimal Control with SciML
date: 2020-06-09
lastmod: 2020-06-09
tags:
  - software
  - julia
summary: Using SciML and Julia for numerical optimized pulse shapes.
draft: false
---

Numerical quantum optimal control is simply optimizing pulse shapes used to drive the control lines on some controllable quantum system to drive that system through some desired state-to-state or unitary transformation. As with any numerical optimization gradient information makes the search much more efficient and not surprisingly two of the more successful approaches have used ways to calculate gradient information along with the evolution.

The Gradient Ascent Pulse Engineering (GRAPE) [^1] approach assumes piece-wise constant pulse amplitudes very similar to an ideal arbitrary waveform generator and then by saving the forwards and backward evolution up to each timestep gradients for the amplitude of the control at each time step are easy to calculate. The original paper used an approximate gradient for the timestep propagator which limited it to small timesteps and/or small Hamiltonians but of course earlier work in NMR had already shown that exact derivatives are available [^2] from diagonalizing the Hamiltonian which may have already been done to calculate the matrix exponential for the propagator.

The Gradient Optimization of Analytic conTrols (GOAT) [^3] algorithm parametrizes the pulse shape as the coefficients of a series of basis functions. This is convenient because implementation constraints such as "the pulse should start and finish at zero amplitude" and bandwidth constraints are easy to enforce in the choice of basis functions itself whereas in GRAPE they need to be implemented as penalty functions. For GOAT the derivatives are calculated by extending the equations of motions to solve for the gradient of the unitary using the gradient of the Hamiltonian which requires some chain rule work.

All the work pouring into automatic differentiation has made implementing these two approaches rather straightforward without any extra work to implement the particular approaches of the GRAPE (saving forward and backwards evolution or GOAT (extending the equations of motion to include the derivative) approaches. The Schuster group has a paper discussing how to apply TensorFlow to GRAPE [^4]. Here, I'll show how we can use parts of the [SciML](https://sciml.ai/) framework in Julia to implement the GOAT approach without having to actually implement GOAT.

The DRAG approach [^5],[^6] for limiting the effects of nearby leakage levels was initially discovered from numerical quantum optimal control. The team was searching for pulse shapes for transmon qubits and kept landing on the same looking pulse which was then later justified by the full DRAG theory. The problem is a great sanity check for any quantum optimal control package: given a three level system --- two qubit levels and a nearby leakage level --- trying to optimize a qubit unitary should give something that looks like a DRAG pulse.

[notebook nbviewer link with plots](https://nbviewer.jupyter.org/gist/caryan/a6883325c5cf3ba0a5ae54fce0645613)

{{<gist caryan a6883325c5cf3ba0a5ae54fce0645613>}}


[^1]: Khaneja, N., Reiss, T., Kehlet, C., Schulte-Herbrüggen, T., & Glaser, S. J. (2005). Optimal control of coupled spin dynamics: design of NMR pulse sequences by gradient ascent algorithms. [Journal of Magnetic Resonance, 172(2), 296–305](https://doi.org/10.1016/j.jmr.2004.11.004).

[^2]: Levante, T. O., Bremi, T., & Ernst, R. R. (1996). Pulse-sequence optimization with analytical derivatives. Application to deuterium decoupling in oriented phases. [Journal of Magnetic Resonance - Series A, 121(2), 167–177() https://doi.org/10.1006/jmra.1996.0157).

[^3]: Machnes, S., Assémat, E., Tannor, D., & Wilhelm, F. K. (2018). Tunable, Flexible, and Efficient Optimization of Control Pulses for Practical Qubits. Physical Review Letters, 120, 150401. https://doi.org/10.1103/PhysRevLett.120.150401

[^4]: Leung, N., Abdelhafez, M., Koch, J., & Schuster, D. (2017). Speedup for quantum optimal control from automatic differentiation based on graphics processing units. [Physical Review A, 95(4), 042318](https://doi.org/10.1103/PhysRevA.95.042318).

[^5]: Motzoi, F., Gambetta, J. M., Rebentrost, P., & Wilhelm, F. K. (2009). Simple Pulses for Elimination of Leakage in Weakly Nonlinear Qubits. [Physical Review Letters, 103 (11), 110501](https://doi.org/10.1103/PhysRevLett.103.110501).

[^6]: Gambetta, J., Motzoi, F., Merkel, S., & Wilhelm, F. (2011). Analytic control methods for high-fidelity unitary operations in a weakly nonlinear oscillator. [Physical Review A, 83(1), 012308](https://doi.org/10.1103/PhysRevA.83.012308).
