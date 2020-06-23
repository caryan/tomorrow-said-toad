---
title: Two approaches to Savitsky-Golay filtering
date: 2019-11-30
lastmod: 2020-02-27
tags:
  - software
  - julia
summary: Comparing matrix inversion and Gram polynomial approaches to Savitsky-Golay filtering.
draft: false
markup: mmark #  mmark is deprecated but needed for Katex for now https://github.com/gohugoio/hugo/issues/6544
---

Savitsky-Golay filtering[^1] is one of my first choices for smoothing noisy experimental data. It has the nice property of preserving higher moments of the data and so particularly for spectroscopy it preserves peak heights [^2]. Savitsky-Golay filtering is a simple enough idea: fit a moving $$n^{th}$$-degree polynomial to a window around each point and then evaluate the polynomial at the mid-point to provide the smoothed value. The key insight of Savitsky-Golay was that we don't have to repeat the least-squares fit for every point: we can write the polynomial coefficients as a linear combination of the data values in the window so that once we know the appropriate weights we can apply the filter as a convolution.

I wanted to work through the usual derivation for the Savitsky-Golay convolution coefficients starting from the design matrix to make sure I understood both the pseudo-inverse approach and how `SciPy` was calculating the filter coefficients for a particular derivative with a matrix-vector least squares inversion. And I also got curious about another approach using a different family of polynomials, the Gram polynomials [^3].

# Calculating filter coefficients with matrix inversions

Using the conventional polynomials $$p_0 + p_1x + p_2x^2 + p_3x^3 + \dots$$ we can cast the polynomial fitting problem in matrix form: $$\mathbf{A}\cdot\mathbf{p} = \mathbf{y}$$ for a column vector of the polynomial coefficients, $$\mathbf{p}$$ and the data in the window to fit $$\mathbf{y}$$. For equally spaced normalized points $$\dots -2, -1, 0, 1, 2, \dots$$ the design matrix $$\mathbf{A}$$ is a [Vandermonde matrix](https://en.wikipedia.org/wiki/Vandermonde_matrix):

$$
\begin{bmatrix}
\vdots & \vdots & \vdots & \vdots &\\
1 & -2 & 4 & -8 & \dots \\
1 & -1 & 1 & -1 & \dots \\
1 &  0 & 0 &  0 & \dots \\
1 &  1 & 1 &  1 & \dots \\
1 &  2 & 4 &  8 & \dots \\
\vdots & \vdots & \vdots & \vdots &\\
\end{bmatrix}
\begin{bmatrix}
p_0 \\
p_1 \\
p_2 \\
p_3 \\
\vdots
\end{bmatrix} =
\begin{bmatrix}
\vdots \\
y_{-2} \\
y_{-1} \\
y_0 \\
y_1 \\
y_2 \\
\vdots
\end{bmatrix}
$$

## Full Pseudo-Inverse

For fitting a $$m^{th}$$ order polynomial to a data window $$w$$ points wide we have a $$\mathbf{A}$$ is a $$w \times (m+1)$$ matrix and we are looking for the pseudo-inverse matrix $$\mathbf{C}$$ ($$(m+1) \times w$$) such that $$\mathbf{CA}$$ is a $$(m+1) \times (m+1)$$ identity matrix and if we left multiply both sides by $$\mathbf{C}$$ then we have the coefficients as a product of a matrix $$\mathbf{C}$$ and the data.

$$
\begin{bmatrix}
p_0 \\
p_1 \\
p_2 \\
p_3 \\
\vdots
\end{bmatrix} =
\mathbf{C}
\begin{bmatrix}
\vdots \\
y_{-2} \\
y_{-1} \\
y_0 \\
y_1 \\
y_2 \\
\vdots
\end{bmatrix}
$$

We are guaranteed the pseudo-inverse exists because $$w > m$$ for the fit to unique and a rectangular $$w \times m$$ Vandermonde matrix with all $$x_i$$ unique (which we have because we have equally spaced points) has maximum rank.

Each row of $$\mathbf{C}$$ gives the coefficients for a particular polynomial coefficient. However, for Savitsky-Golay we have a moving window and we only need to evaluate the window at the middle point where $$x=0$$ and so all the $$p_i, i>0$$ don't matter and we only need the first row. Hence we only need a single row of the matrix. Taking the $$n$$'th derivative of the smoothed signal just shifts the coefficients with a factorial scaling and accounting for the x-point spacing. For example the 1st derivative will be $$p_1 + 2p_2x + 3p_3x^2 + \dots$$ so for $$x=0$$ we only need to evaluate the $$p_1$$ term or the first row.

## Solving for a only a single row of coefficients

We can take advantage of that by least-squares solving for only a single row of $$\mathbf{C}$$. We're looking to solve $$\mathbf{CA} = \mathbf{I}$$ and taking the transpose to put it in the conventional $$\mathbf{AX} = \mathbf{B}$$ we have $$\mathbf{A}^\mathrm{T}\mathbf{C}^\mathrm{T} = \mathbf{I}$$ or $$\mathbf{C}^\mathrm{T} = \mathbf{A}^\mathrm{T} \backslash \mathbf{I}$$. We can then solve for say only the first column of $$\mathbf{C}^\mathrm{T}$$ with

$$
\vec{C}_0 = \mathbf{A}^\mathrm{T} \backslash
\begin{bmatrix}
1 \\
0 \\
0 \\
0 \\
\vdots
\end{bmatrix}
$$

# Calculating filter coefficients with orthogonal polynomials

I was intrigued with a second approach using [discrete Chebyshev polynomials or Gram polynomials](https://en.wikipedia.org/wiki/Discrete_Chebyshev_polynomials) because it promised a closed form solution [^3] for all points in the window (as opposed to just the midpoint). This is particularly convenient at the edges. The paper provides a recursive formula for the full table of weights for every data point to evaluate the least squares fit at every point in the window. I have implemented this in the notebook but at first pass it seems rather slow and only of utility if you don't have access to matrix inversion routines. E.g. there appears to be a [C++ implementation](https://github.com/arntanguy/gram_savitzky_golay).

# Corrections to the original Savitsky-Golay

Gorry's paper also pointed out a subsequent paper [^4] that corrected many of the tables in the original Savitsky-Golay paper with the particularly harsh comment:

> The corrected values are presented in Table I. Also, Tables II, III, IV, V, and VI are corrected versions of Tables V, VII, IX, X, and XI given by Savitzky and Golay (I). They either contain more numerous errors or are systematically false.


# Julia Notebook Demo

I put together a little notebook demoing and benchmarking the two approaches. There are probably plenty of optimizations to be made to the Gram polynomial approach but if we have access to good matrix inversion routines then there does not seem to be any advantage to using Gram polynomials as it's a couple of orders of magnitude slower.

<script src="https://gist.github.com/caryan/6cb5be4bf7e0306dc236c3688e548d68.js"></script>

[^1]: Savitzky, A., & Golay, M. J. E. (1964). Smoothing and Differentiation of Data by Simplified Least Squares Procedures. [Analytical Chemistry, 36(8), 1627–1639](https://doi.org/10.1021/ac60214a047).

[^2]: Press, W. H., & Teukolsky, S. A. (1990). Savitzky-Golay Smoothing Filters. [Computers in Physics, 4(6), 669](https://doi.org/10.1063/1.4822961).

[^3]: Gorry, P. A. (1990). General Least-Squares Smoothing and Differentiation by the Convolution (Savitzky-Golay) Method. [Analytical Chemistry, 62(6), 570–573](https://doi.org/10.1021/ac00205a007).

[^4]: Steinier, J., Termonia, Y., & Deltour, J. (1972). Comments on Smoothing and differentiation of data by simplified least square procedure. [Analytical Chemistry, 44(11), 1906–1909](https://doi.org/10.1021/ac60319a045)
