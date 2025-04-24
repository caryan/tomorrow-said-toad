---
title: "When Two Wrongs Make a Right"
date: 2025-03-25
lastmod: 2025-04-23
tags:
  - information theory
summary: What is the probability of observing a bitflip if two bitflips cancel?
draft: false
---

In our quantum computers we have errors on our qubits, bit-flips or phase-flips, that occur at some high rate. However, we do not observe every flip: we run a memory experiment where we initialize the qubit, try to preserve the information for some interval of time, and then observe whether the final state is the same as the initialized state. If there was two flips they cancel out and we observe no error. I often forget and have to rederive how to connect the expected fidelity decay to the bit/phase-flip rate. 

If we start in a fiducial state and then apply bit-flips at some rate we only observe the bit flipped after some time interval if there is an *odd* number of bit-flips. The number of bitfips in the time interval will follow the [Poisson distribution](https://en.wikipedia.org/wiki/Poisson_distribution) where the probability of \(k\) bit-flips that come at an average rate \(\Gamma\) in an interval \(t\) is given by

\[
P(k) = \frac{\lambda^k e^{-\lambda }}{k!},
\]

where \(\lambda = \Gamma t\) is the mean number of flips in interval. The probability of observing a bitflip is the probability of an odd number of flips or 

\[
P_\text{flip} = \sum_{k \text{ odd}}P_k 
= \sum_{k \text{ odd}} \frac{\lambda^k e^{-\lambda}}{k!}
= e^{-\lambda} \sum_{k \text{ odd}} \frac{\lambda^k}{k!}.
\]

The trick then is that the sum looks like half the terms in the Taylor expansion of the exponential function \(e^{x} = \sum_{k=0}^{\infty} \frac{x^k}{k!}\) and that we can get to half the terms because in the expansion of \(e^{-x} = \sum_{k=0}^{\infty} \frac{(-1)^k x^k}{k!} \) every other term is negative. Then

\[
\sum_{k \text{ odd}} \frac{\lambda^k}{k!} = \frac{e^{\lambda} - e^{-\lambda}}{2}.
\]

Putting this back into the expression for \(P_\text{flip}\)

\[
\begin{aligned}
P_\text{flip} &= e^{-\lambda} \sum_{k \text{ odd}} \frac{\lambda^k}{k!}\\
&=  e^{-\lambda} \frac{e^{\lambda} - e^{-\lambda}}{2} \\
&= \frac{1}{2}\left(1 - e^{-2\lambda}\right) \\
&= \frac{1}{2}\left(1 - e^{-2\Gamma t}\right)
\end{aligned}
\]

Which behaves as expected:
1. At long times we expect a completely randomized or 50% chance of observing a bitfip;
2. At short times we expect to rarely see more than 1 bit flip and we should be close to the average \(\Gamma t\). Indeed, the linear expansion of the exponential gives \(P_\text{flip} = \frac{1}{2}\left(1 - \left(1 - 2\Gamma t\right)\right) = \Gamma t \)

As noted in the supplementary of the Google d=7 paper [arXiv:2408.13687](https://arxiv.org/abs/2408.13687) similar logic applies is the discrete time situation when converting error per syndrome round to a observed error rate after many rounds where the we move from the sum of odd terms the Poisson distribution to the sum of odd terms in the binomial distribution. If \(p\) is the probability of bitflip per round then the the number of flips after \(n\) rounds follow the binomial distribution and the probability of the final state being flipped after n rounds  \(P_\text{flip} = \sum_{k \text{ odd}} \binom{n}{k} p^k\left(1-p\right)^{n-k}\) The trick here is this looks just like half the terms in binomial formula for \(\left(x + y\right)^n = \sum_{k=0}^n \binom{n}{k} x^{k}y^{n-k}\) where \(x=1-p\) and \(y = p\). If we also consider \(y=-p\) and take the difference \((1 - p + p)^n - (1 - p - p)^n\) we get the sum of odd terms we want. Since \((1 - p + p)^n = 1^n = 1\), as it should since the binomial probability distribution should sum to 1, then 

\[
P_\text{flip} = \sum_{k \text{ odd}}\binom{n}{k} p^k\left(1-p\right)^{n-k} = \frac{1}{2}\left(1 - (1 - 2p)^n\right)
\]

## Should I even write these down anymore?

Of course recently when I forget I ask an LLM and this has improved dramatically over the past couple years. As an aside it seems difficult to go back and check how old commerical models perform -- they just disappear. It used to bobble and middirect me on it but now it is not even clear that it is worth writing this down anymore. Claude 3.7 thinking nails it on the first try [link](https://claude.ai/share/d868dee3-bc4a-4443-a6cf-1757e971702b).

> If I have a bit that is flipped with some probability p every round what is the probability that the bit is flipped after n rounds?
>
> To solve this problem, I need to find the probability that a bit's state is different from its initial state after n rounds, where in each round it has probability p of being flipped.
>
> The key insight is that the bit ends up in a flipped state if and only if it experiences an odd number of flips during the n rounds.
>
> Let me derive the formula:
>
> For a bit to be flipped after n rounds, it must be flipped an odd number of times: 1, 3, 5, etc.
> 
> Using the binomial distribution, the probability of the bit being flipped exactly k times in n rounds is:
$P(k \text{ flips}) = \binom{n}{k} p^k (1-p)^{n-k}$
>
> The total probability of the bit being flipped after n rounds is the sum of probabilities for all odd values of k:
$P(\text{flipped}) = \sum_{k \text{ odd}} \binom{n}{k} p^k (1-p)^{n-k}$
>
> This sum can be simplified using properties of the binomial theorem. After working through the algebra:
>
> $$P(\text{flipped after n rounds}) = \frac{1 - (1-2p)^n}{2}$$
>
> We can verify this makes sense:
> - If p = 0 (never flips): result is 0
> - If p = 1 (always flips): result is 0 for even n and 1 for odd n
> - If p = 0.5: result is 0.5 for n > 0
>
> This formula gives us the probability that the bit's final state differs from its initial state after n rounds.

And you can see in the thinking portion is is using exactly the trick above or another trick involving the probability generating function.
