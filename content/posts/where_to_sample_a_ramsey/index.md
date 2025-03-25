---
title: Where to sample a Ramsey experiment
date: 2020-06-30
lastmod: 2020-06-30
tags:
  - information theory
  - software
  - julia
summary: The tradeoff between sensitivity and shot noise
draft: false
---

Let's take a look at the experimental design problem of choosing the sampling points when  estimating frequency with a Ramsey experiment. The intuitive result is that we should measure at the point of maximum slope to maximize our sensitivity. However, when measuring a qubit we will run into a tradeoff between sensitivity and projection noise. We will work through the surprising result that these two effects perfectly balance such that all sampling points give the same information.

# Ramsey Sequence

A time-domain Ramsey experiment is typically used to measure the frequency (and \(T_2\)) of a qubit. We start with the qubit in the ground state, apply a \(X_{90}\) pulse to create a superposition of |0⟩ and |1⟩ with a defined phase, let the superposition evolve for some time \(t\), apply a second \(X_{90}\) to convert the phase of the superposition in a population that can be read out. If the qubit is detuned with respect to the frame of the drive by a frequency \(f\) then the probability of measuring a |1⟩ goes as \(\cos(2\pi ft/2)^2\).

If we convert \(f\) and \(t\) to some accumulated phase \(\theta\) then the idealized Ramsey signal is a simple sinusoid and measuring the sinusoid gives us information about the qubit frequency. Intuitively, to maximize the information gained from the experiment we want to sample at the maximum slope at \(\theta = \frac{\pi}{2}\) or \(\theta = \frac{3\pi}{2}\) where small changes in phase lead to large changes in the measurement outcome and vice-versa we do not want to measure at the extrema at 0 or \(\pi\) where small changes in frequency will change the probability of |1⟩ very little.  And so if we have a good prior for the frequency we should choose our sampling time to give us the maximum sensitivity.

{{< figure src="ramsey_fringe.svg" width="100%">}}

We can visualize this by adding Gaussian noise on top of the Ramsey fringe sinusoid and looking at the likelihood distribution for \(\theta\) given we measured the probability of |1⟩ to be \(x\). Near the extrema at 0 or 1 the likelihood is broad and so our uncertainty about \(\theta\) is still large whereas at the points of maximum slope the likelihood is sharply peaked and so we have more more information about \(\theta\).

{{< figure src="likelihood.svg" width="100%">}}


However, if we are measuring a qubit then there is an additional wrinkle: the points of maximum slope come at the 50% probability of |1⟩ when the qubit is left in an equal superposition state. Measuring a qubit gives binary outcomes like coin flips and at this 50% point we have maximum variance in the outcome and so we would expect less information. The information coming from the slope of the Ramsey curve is fighting against the variance from the projection noise. We will show that surprisingly these two effects perfectly cancel out.


# Fisher Information

We will start with some random variable \(X\) we are measuring that depends on an unknown parameter \(\theta\) and we are trying to use the measurements of \(X\) to infer \(\theta\). The Fisher information makes concrete the intuition that regions of steep slope or sharp peaks in the output probability versus \(\theta\) as will have much more information than flat regions. If the probability density/mass function for getting some output \(x\) given \(\theta\) is \(f(x|\theta)\). then the Fisher information is the variance of the partial derivative of \(f(x|\theta)\):

$$
\mathcal{I(\theta)} = E\left[ \left(\frac{\partial}{\partial\theta} \log f(x|\theta) \right)^2 \right] = \int dx \left( \frac{\partial}{\partial\theta} \log f(x|\theta)\right)^2 f(x|\theta)
$$

If we can take the second derivative then:

$$
\frac{\partial ^2}{\partial\theta ^2} \log f(x|\theta)
= \frac{\partial}{\partial\theta} \left( \frac{ \frac{\partial}{\partial\theta } f(x|\theta) } {f(x|\theta)} \right)
= \frac{\frac{\partial ^2}{\partial\theta ^2} f(x|\theta)}{f(x|\theta)} - \frac{(\frac{\partial}{\partial\theta } f(x|\theta))^2}{f(x|\theta) ^2}
$$

If we then take an expectation value over \(x\) then the first term vanishes:

$$
E\left[ \frac{\frac{\partial ^2}{\partial\theta ^2} f(x|\theta)}{f(x|\theta)} \right]
= \int dx \frac{\frac{\partial ^2}{\partial\theta ^2} f(x|\theta)}{f(x|\theta)} f(x|\theta)
= \frac{\partial ^2}{\partial\theta ^2} \int dx f(x|\theta)
= \frac{\partial ^2}{\partial\theta ^2} 1
= 0
$$

and the second term equals the integrand in \(\mathcal{I}(\theta)\) as defined above so

$$
\mathcal{I(\theta)} = -E\left[ \frac{\partial ^2}{\partial\theta ^2} \log f(x|\theta) \right]
$$

This nicely quantifies the intuition above that we are looking for sharply peaked regions of the likelihood.

## Fisher Information for a Bernoulli trial

Take \(f(x|\theta)\) to for a Bernouilli trial i.e. the outcomes are either 0 or 1 and the underlying parameter we are trying to estimate, \(\theta\), is the probability of getting a 1.

$$
f(x|\theta) = θ^x (1-θ)^{1-x}
$$

Then

$$
\begin{aligned}
\frac{\partial^2}{\partial\theta^2} \log f(x|\theta)
&= \frac{\partial^2}{\partial\theta^2} \left( x\log\theta + (1-x)\log(1-\theta) \right) \\
&= -\frac{x}{\theta^2} - \frac{1-x}{(1-\theta)^2}
\end{aligned}
$$

If we take the expectation value over \(x\) then this becomes a discrete sum or we can just push the expectation value into \(E[x] = \theta\) so

$$
\begin{aligned}
\mathcal{I}(\theta) &= -E\left[-\frac{x}{\theta^2} - \frac{1-x}{(1-\theta)^2}\right] \\
&= \frac{E[x]}{\theta^2} - \frac{1-E[x]}{(1-\theta)^2} \\
&= \frac{1}{\theta} + \frac{1}{1-\theta} \\
&= \frac{1}{\theta(1-\theta)}
\end{aligned}
$$

Hence, we expect the Fisher information to go to infinity as θ goes to either 0 or 1 and reaches a minimum of 4 at the 50:50 probability point.

{{< figure src="fisher_information_bernoulli.svg" width="100%">}}


## Fisher information for a sinusoid with additive Gaussian noise

If we go back to a sinusoid with noise independent of \(\theta\) then we can confirm the original intuition that the most information comes at the slope. If we assume independent Gaussian noise on top of a sinusoid and take \(N(\mu, \sigma^2)\) to be the normal distribution with mean \(\mu\) and variance \(\sigma^2\) then \(f(x|θ) = N(\cos\theta, σ^2)\) and

$$
\begin{aligned}
\frac{\partial^2}{\partial\theta^2} \log f(x|\theta)
&= \frac{\partial^2}{\partial\theta^2} \log \left( \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{1}{2} \left(\frac{x-\cos\theta}{\sigma}\right)^2 \right) \right) \\
&= \frac{\partial^2}{\partial\theta^2}\left(\log(\frac{1}{2σ\sqrt{2\pi}}) -\frac{1}{2\sigma^2} \left(x-\cos\theta\right)^2 \right) \\
&= -\frac{1}{\sigma^2}\frac{\partial}{\partial\theta}\left(\left(x-\cos\theta\right)\sin\theta\right) \\
&= -\frac{1}{\sigma^2}\left(x\cos\theta - \cos(2\theta) \right)
\end{aligned}
$$

Then taking the expectation value to get the Fisher information (and using the both that the expectation value of \(x\) is the mean value \(\cos\theta\) and the double angle identity)

$$
\begin{aligned}
\mathcal{I}(\theta)
&= -E\left[-\frac{1}{\sigma^2}\left(x\cos\theta - \cos(2\theta) \right)\right] \\
&= \frac{1}{\sigma^2}\left(E[x]\cos\theta - \cos(2\theta)\right) \\
&= \frac{1}{\sigma^2}\left(\cos^2\theta - (\cos^2\theta - \sin^2\theta) \right) \\
&= \frac{1}{\sigma^2}\sin^2\theta
\end{aligned}
$$


{{< figure src="fisher_information_sinusoid_gaussian.svg" width="100%">}}

# Fisher Information in a Ramsey Experiment

Finally we look at the Fisher information for a Bernouilli trial where the success probability (probability of measuring a 1) goes as the Ramsey fringe probability \(\cos^2\left(\frac{\theta}{2}\right)\) where \(\theta\) is the accumulated phase during the Ramsey free evolution. Therefore,

$$
\log f(x|\theta) = x \log \left(\cos^2\left(\frac{\theta}{2}\right)\right) + (1-x)\log\left(1-\cos^2\left(\frac{\theta}{2}\right)\right)
$$

and

$$
\begin{aligned}
\frac{\partial^2}{\partial\theta^2} \log f(x|\theta)
&= \frac{\partial}{\partial\theta}\left[2x\frac{-\frac{1}{2}\sin\left(\frac{\theta}{2}\right)}{\cos\left(\frac{\theta}{2}\right)} + (1-x)\frac{\cos\left(\frac{\theta}{2}\right)\sin\left(\frac{\theta}{2}\right)}{1-\cos^2\left(\frac{\theta}{2}\right)}\right] \\
&= \frac{\partial}{\partial\theta}\left[-x\tan\left(\frac{\theta}{2}\right) + (1-x)\cot\left(\frac{\theta}{2}\right) \right] \\
&= \frac{-x}{2\cos^2\left(\frac{\theta}{2}\right)} + \frac{-(1-x)}{2\sin^2\left(\frac{\theta}{2}\right)}
\end{aligned}
$$

Finally we can evaluate the Fisher information by taking the expectation value over \(x\) and using the fact that \(E[x] = \cos^2\left(\frac{\theta}{2}\right)\)

$$
\begin{aligned}
\mathcal{I}(\theta)
&= -E\left[ \frac{-x}{2\cos^2\left(\frac{\theta}{2}\right)} + \frac{-(1-x)}{2\sin^2\left(\frac{\theta}{2}\right)} \right] \\
&= 1
\end{aligned}
$$

And so we arrive at the surprising result that the contributions to the Fisher information from the sinusoid and Bernoulli terms perfectly cancel leaving a constant Fisher information. Of course this is only for the case of perfect projection noise. In some experiments with low single shot readout fidelity there will be a mixture of Gaussian and projection noise and there will be an advantage to optimizing the sampling.

{{< figure src="fisher_information_sinusoid_projection.svg" width="100%">}}

# Julia Notebook

Calculating the Fisher information requires taking derivatives of the log-likelihood and so it was a fun excuse to use the [Zygote.jl](https://github.com/FluxML/Zygote.jl) automatic differentiation package in Julia. I was impressed that with [Distributions.jl](https://github.com/JuliaStats/Distributions.jl) augmented with [DistributionsAD.jl](https://github.com/TuringLang/DistributionsAD.jl) I could easily take derivatives of the `logpdf` of a distribution. The notebook has a function for numerically calculating the Fisher information and generates the plots above.

[nbviewer with plots](https://nbviewer.jupyter.org/gist/caryan/75f6b0d48472de2a610b0a2d50510a25)

{{<gist caryan 75f6b0d48472de2a610b0a2d50510a25>}}
