---
title: Python function call overhead
date: 2020-06-17
lastmod: 2020-06-17
tags:
  - software
  - python
summary: Measuring function call overhead from Python 2.7 to 3.8
draft: false
---

Wrapping some piece of logic in a function provides all the promised benefits: code reuse, scope isolation, unit-testing boundary, etc. However, as always, there are no unalloyed goods and I'm particulary partial to Cindy Sridharan's [Small Functions considered Harmful](https://medium.com/@copyconstruct/small-functions-considered-harmful-91035d316c29) take on the harms of taking this too far. There is also a non-zero performance penalty where there is no optimizing compilier to inline function calls and out of curiousity I wanted to look what this performance penalty is for Python by trying to measure the overhead of Python functions.

I am quite sure there are some benchmarking boobytraps I'm missing, but the approach I took to measure function call overhead was to make a series of increasingly nested function calls and then time how long each one took. For example, if we define

```python
def a():
    return 29

def b():
    return a()

def c():
    return b()
```

then by timing how much longer `b()` takes than `a()` and `c()` than `b()` and so on then can attribute that increase to function call overhead

We can then repeat the pattern of nested function calls for a few different types of functions:
1. Plain no-argument functions (as above).
2. 1 argument functions to see how expensive passing arguments is.
3. Instance methods with no arguments to check the overhead of adding classes to the mix.
4. Instance methods with 1 argument.

The code for the remaining cases looks something like:

```python
def times2_a(x):
    return 2*x

def times2_b(x):
    return times2_a(x)

def times2_c(x):
    return times2_b(x)

class OneLiners():
    def a(self):
        return 29

    def b(self):
        return self.a()

    def c(self):
        return self.b()

    def times2_a(self, x):
        return 2*x

    def times2_b(self, x):
        return self.times2_a(x)

    def times2_c(self, x):
        return self.times2_b(x)
```

We can then time everything using [iPython's `timeit` magic](https://ipython.readthedocs.io/en/stable/interactive/magics.html#magic-timeit).

```python
timing_results = {}

timing_results['Function No Arg'] = []

ti = %timeit -o -q a()
timing_results['Function No Arg'].append(ti)

ti = %timeit -o -q b()
timing_results['Function No Arg'].append(ti)

⋮
```

And plot the timing results as function time versus function depth (up to 10) and run some simple linear regression to estimate the slope in order to extract the overhead per function call assuming it is constant with stack size.

```python
fig,ax = plt.subplots(figsize=(10,6))

overheads = {}
max_depth = 10

# explicit order because dictionary order is only preserved for Python 3.6+
for ct, label in enumerate(('Function No Arg', 'Function 1 Arg', 'Class Method No Arg', 'Class Method 1 Arg')):
    results = timing_results[label]
    xs = 1 + np.arange(max_depth)
    # the results from timeit changed at some point
#     vals = np.array([ti.average/1e-9 for ti in results])
#     errs = np.array([ti.stdev/1e-9 for ti in results])
    vals = np.array([np.mean(ti.all_runs)/ti.loops/1e-9 for ti in results])
    errs = np.array([np.std(ti.all_runs)/ti.loops/1e-9 for ti in results])
    fit_coeffs, V = np.polyfit(xs, vals, deg=1, cov=True, w=1/errs)
    overheads[label] = (fit_coeffs[0], np.sqrt(V[0,0]))
    err_bars = ax.errorbar(xs, vals, yerr=errs, linestyle="none", elinewidth=3, marker=".", label=label+" | {:.0f} +- {:.0f} ns".format(overheads[label][0],overheads[label][1]), color="C{}".format(ct))
    ax.plot(xs, np.poly1d(fit_coeffs)(xs))
    ax.set_xlabel("Function Depth")
    ax.set_ylabel("Overhead (ns)")
    ax.set_title("Function Call Overhead in Python {}".format(platform.python_version()))

plt.legend(loc="upper center")
plt.savefig("function_call_overheads_{}.svg".format(platform.python_version()))
```

We get typical plots like below for Python 3.8. There are some outliers with large uncertainty which I attribute to not being careful about making sure there was nothing else going on. The results are not as linear as I expected. Particularly for the "Function No Arg" case there seems to be a step around a depth of 5 and and the error bars are inconsistent with the linear model. Nevertheless, the approach gives reproducible results over multiple runs.

{{< figure src="function_call_overheads_3.8.3.svg" width="100%">}}

The results consistently show a function call overhead in the 50-100 ns range and increasing overhead with either function arguments or using class methods. If some code is only making a few function calls and trying to perform logic on a human timescale of many 10's of ms then this overhead of 10's of nanoseconds is probably immaterial. However, if you're applying some small function to many millions of array elements then this overhead is very material. Of course going fast in array processing in Python is all about avoiding this penalty and calling out to C via e.g. `numpy`.

Finally we can rerun this overhead analysis for several recent versions of Python 3 and Python 2.7 to see how the optimizations made have changed the situation. Bundling the results by either function type or Python version we see:

{{< figure src="function_call_overhead_grouped_by_type.svg" width="100%">}}

{{< figure src="function_call_overhead_grouped_by_version.svg" width="100%">}}

The overall picture is that the gap between bare functions and class methods appears to being squeezed out. Presumably the big improvement from Python 3.6 to 3.7 came from specific [optimizations](https://docs.python.org/3/whatsnew/3.7.html#optimizations)

> Method calls are now up to 20% faster due to the bytecode changes which avoid creating bound method instances.

The entire notebook is available on [nbviewer](https://nbviewer.jupyter.org/gist/caryan/4a2c94a62e9da5b18eaed62fb637fc4a)
