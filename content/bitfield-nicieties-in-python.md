Title: Bitfield nicities in Python
Date: 2016-2-08
Modified: 2016-2-08
Category: Python

With code contributions from [Graham Rowlands](http://www.grahamerowlands.com/).

For low level device drivers or communications protocols it's handy to be able
to bounce the individual bits in an integer around as several fields might be packed into a larger
integer in a [bitfield](https://en.wikipedia.org/wiki/Bit_field).

There are, of course, already several ways to tackle this in Python:

1. Python's built in ctypes module already [supports
bitfields](https://docs.python.org/3.5/library/ctypes.html#structures-and-unions)
using the `__fields__` attribute.
1. There are a number of Python modules such as [bitstring](http://scott-griffiths.github.io/bitstring/), [ctypes-bitfield](https://pypi.python.org/pypi/ctypes-bitfield) or [code examples](http://code.activestate.com/recipes/113799/)

But of course none of these did exactly what I wanted which a was a clean way to
define a bitfield and then use it with some error checking.

Fortunately some metaprogramming give a very clean interface.

## Implementation

We first define class to represent the fields we want to pack.  All it has is a
width which is the width of the field in bits. All of this is for Python 3.

```python
class BitField(object):
    """Bit field in a bit field union"""
    def __init__(self, width):
        super(BitField, self).__init__()
        self.width = width
```

Then we define a metaclass for our union of a set of bitfields and the packed
integer representation. We use a metaclass so that we can muck with the class
dictionary and parse the class variables.

```python
class BitFieldUnionMeta(type):
    """Metaclass for injecting bitfield descriptors"""
    @classmethod
    def __prepare__(metacls, name, bases):
        return collections.OrderedDict()

    def __init__(self, name, bases, dct):
        type.__init__(self, name, bases, dct)
        self.packed = 0
        init_offset = 0
        for k,v in dct.items():
            if isinstance(v, BitField):
                def fget(self, offset=init_offset, width=v.width):
                    return (self.packed >> offset) & (2**width-1)
                def fset(self, val, offset=init_offset, width=v.width):
                    #check we don't exceed the width of the field
                    if (val & (2**width-1)) != val:
                        err_msg = "attempted to assign value that does not fit in bit field width {:d}".format(width)
                        raise ValueError(err_msg)
                    self.packed &= ~((2**width-1) << offset) #clear the field
                    self.packed |= (val & (2**width-1)) << offset #set the field
                setattr(self, k, property(fget, fset, None, None))
                init_offset += v.width
```

There is a lot going on here so let's go through it step by step.

1. It's a metaclass so we subclass `type`.
1. We define the class `__prepare__` method (which is called during class
creation to ["prepare the class
namespace"](https://docs.python.org/3/reference/datamodel.html#preparing-the-class-namespace)
or essentially the class dictionary) so that we can use an ordered dictionary.
This ensures that we pack the bits in the order in which they are defined.
1. Finally in `__init__` method, called when initializing the already instantiated metaclass, we then parse all the class variables.  If it is a BitField then we define:
    1. a getter which slices out the appropriate bits
    1. a setter which checks for overflow and then sets the appropriate slice
    1. create a property for the field using the getter/setter
    1. update the offset into the `packed` value - we're assuming an explicit ordering here to the packing.

Finally we create wrapper class to hide the metaclass and provide some keyword constructor nicities.

```python
class BitFieldUnion(metaclass=BitFieldUnionMeta):
    """Painless bit packing"""
    def __init__(self, **kwargs):
        super(BitFieldUnion, self).__init__()
        if "packed" in kwargs and len(kwargs) > 1:
            raise AttributeError("unable to set both `packed` and another bit field")
        for k,v in kwargs.items():
            setattr(self, k, v)
```

## Usage

Now we can play with a sample. We might have arbitrary waveform generator that plays sequences that are lists of segments.  Each 32 bit command word packed the following way:

* bits [15:0] segment loop count
* bit 16 start sequence flag
* bit 17 stop sequence flag
* bits [21:18] sequence mode
* bits [30:22] reserved
* bit 31 marker enable

We could create a class representing the command words as

```python
In [2]: class SequenceControlWord(BitFieldUnion):
   ...:       segment_loop_count  = BitField(16)
   ...:       sequence_start_flag = BitField(1)
   ...:       sequence_stop_flag  = BitField(1)
   ...:       sequence_mode       = BitField(4)
   ...:       reserved            = BitField(9)
   ...:       marker_enable       = BitField(1)
   ...:     
```

And use it...

```python
In [3]: ctrl_word = SequenceControlWord(segment_loop_count=0xabc, sequence_stop_flag=1, marker_enable=1)

In [4]: format(ctrl_word.packed, "#08x")
Out[4]: '0x80020abc'

In [5]: ctrl_word.sequence_mode = 16
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
<ipython-input-9-a93d8ebd2cfd> in <module>()
----> 1 ctrl_word.sequence_mode = 16

..../binutils.py in fset(self, val, offset, width)
     25                     if (val & (2**width-1)) != val:
     26                         err_msg = "attempted to assign value that does not fit in bit field width {:d}".format(width)
---> 27                         raise ValueError(err_msg)
     28                     self.packed &= ~((2**width-1) << offset) #clear the field
     29                     self.packed |= (val & (2**width-1)) << offset #set the field

ValueError: attempted to assign value that does not fit in bit field width 4

```

## References
1. [Python 3 Metaprogramming](http://www.dabeaz.com/py3meta/Py3Meta.pdf)
