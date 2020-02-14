---
title: Reflection to discover function keyword arguments in Julia
date: 2017-01-12
tags:
  - software
  - julia
summary: Extracting named keyword arguments from a function in Julia
draft: false
---

I needed to extract the named keyword arguments for a function in Julia. In
Python we have the
[inspect.getargspec](https://docs.python.org/3.5/library/inspect.html#inspect.getargspec)
function but in Julia there doesn't seem to be any standard way to do so.
Obviously it's possible because calling `methods` on a function lists them at
the REPL.

```julia
julia> versioninfo()
Julia Version 0.5.0
Commit 3c9d753 (2016-09-19 18:14 UTC)
Platform Info:
  System: Linux (x86_64-linux-gnu)
  CPU: Intel(R) Xeon(R) CPU E3-1505M v5 @ 2.80GHz
  WORD_SIZE: 64
  BLAS: libopenblas (USE64BITINT DYNAMIC_ARCH NO_AFFINITY Haswell)
  LAPACK: libopenblas64_
  LIBM: libopenlibm
  LLVM: libLLVM-3.7.1 (ORCJIT, broadwell)

julia> using Clustering

julia> methods(kmeans)
# 1 method for generic function "kmeans":
kmeans(X::Array{T<:Any,2}, k::Int64; weights, init, maxiter, tol, display) at /home/cryan/.julia/v0.5/Clustering/src/kmeans.jl:49
...
```

Digging through `methodsshow.jl` in `Base` we can pull the three lines that do
what we want.

```julia
julia> ml = methods(kmeans)
# 1 method for generic function "kmeans":
kmeans(X::Array{T<:Any,2}, k::Int64; weights, init, maxiter, tol, display) at /home/cryan/.julia/v0.5/Clustering/src/kmeans.jl:49

julia> m = collect(ml)[1]
kmeans(X::Array{T<:Any,2}, k::Int64) at /home/cryan/.julia/v0.5/Clustering/src/kmeans.jl:49

julia> kwargs = Base.kwarg_decl(m.sig, typeof(ml.mt.kwsorter))
5-element Array{Any,1}:
 :weights
 :init   
 :maxiter
 :tol    
 :display

```

Since this is not exported from `Base` there is no guarantee it will work in
future versions of Julia.
