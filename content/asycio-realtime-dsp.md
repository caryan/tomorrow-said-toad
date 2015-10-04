Title: asycio real-time signal processing
Date: 2015-09-20
Modified: 2015-10-03
Status: Draft
Category: Python

I'm taken with using Python's relatively recent asycio module for real-time DSP.
This isn't because it looks particularly efficient but because it looks very
similar to how we do DSP on an FPGA. Of course we won't actually get the massive
parallelism of a real FPGA but by setting up all our coroutines at the start and
letting things go, the data will naturally flow through the processing chain and
handle back pressure without any particular intervention or scheduling by us.
This also allows us to tap into the the data stream at any point for addition
processing, plotting or saving.

In FPGA land we have all our DSP (FIR filtering, demodulating, decimating etc.)
as modules that takes streams of data (AXI streams) and every clock cycle
they'll process data with something like:

```VHDL
if rising_edge(clk) and data_vld = '1' then
	process_data....
end if;
```

All the modules are connected by FIFOs that allow the system to cross clock
domains and soak up back-pressure if the system is producing data faster than it
can be processed. Of course if the system is continually taking data faster than
processing we'll run into an issue but for short burst of data this works well
as the chains of FIFO's just absorb the pressure without any additional
thinking.

With Python's asyncio co-routines and Queues we should be able to setup
something very similar. Let's setup a simple class structure with
``DataProducer``'s,  ``DataCrucher``'s, ``DataPlotters``'s, and ``DataWriters``.

A ``DataProducer`` is anything that produces data that can be consumed by
anything else.  At the start this may be an ADC but in a chain of filters each
element is a ``DataCruncher`` that also acts as a ``DataProducer`` for next
element in the chain.  Let's make a fake ADC that takes data up to a timeout
and then finishes.

```python
class DataProducer(object):
	queue

class ADC(DataProducer):

    async def take_data(self, loop, timeout):
        end_time = loop.time() + timeout
        while True:
			data = np.random.rand(10)
            logging.info("Acquired data and putting in queue")
            await self.queue.put("Queue has data at " + timeStamp )
            if (loop.time() + 1.0) >= end_time:
                shutdown(loop)
                break
            await asyncio.sleep(1)
```

A ``DataProducer`` has a queue that it pushes data to.  The data will be
correctly routed by a ``DataInterconnect`` later. We define the ``take_data``
method as an async co-routine using the new

class DataCrucher(DataProducer):
	pass

```

In Python the FIFOs will be handled by
[asyncio.Queue](https://docs.python.org/3/library/asyncio-queue.html)
