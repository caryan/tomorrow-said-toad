Title: Asyncio Socket Pool
Date: 2019-08-12
Modified: 2019-08-12
Category: Software
Tags: Python

A physics experiment is often a bundle of instrument settings and often there are times when some
particular command may take a long time --- e.g. waiting for some output to settle --- and so we
would like to be able to move on to the next setting. If the instrument communication is over a TCP
socket then there are two common paths:
1. We can make the the interface asynchronous so that it is able to take a whole series of requests
and respond to them out of order.
2. Another possibility is that instrument can support multiple socket connections, but each one is blocking and so we can parallelize communications across the multiple sockets.

Here is a simple implementation of a socket pool wrapped an an [asynccontextmanager
decorator](https://docs.python.org/3/library/contextlib.html#contextlib.asynccontextmanager) so that
we can nicely `async with ...` `await` on the next available socket. To bound the number of open
connection we use an [asyncio
Semaphore](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore). The semaphore is
an integer that is intialized to the maximum number of sockets. Every time a socket is checked out
from the pool the integer is decremented by one and then finally the semaphore blocks when the
integer would go negative. When we are done with the socket we return it to the pool and increment
the integer again. This is all nicely handled with another `asynccontextmanager` so all the
bookkeeping is handled with a simple `async with self.semaphore:`

```python
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, Tuple

class SocketPool():
    """
    A pool of socket connections to some device
    """
    address: str
    """ Hostname for the instrument """

    port: int = 1234
    """ Port that the instrument is listening for connections on. """

    max_num_sockets: int = 10
    """ Maximum number of open sockets to the instrument """

    semaphore: asyncio.Semaphore
    """ Use a semaphore to bound the number of open connection to `max_num_sockets` """

    pool: list
    """ List of socket StreamReader, StreamWriter pairs """

    def __init__(self, address: str, max_num_sockets: Optional[int] = None, port: Optional[int] = None):
        self.address = address

        if max_num_sockets is not None:
            self.max_num_sockets = max_num_sockets

        if port is not None:
            self.port = port

        self.semaphore = asyncio.Semaphore(self.max_num_sockets)

        self.pool = []

    @asynccontextmanager
    async def get_socket(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """
        Get the next available socket reader/writer from the pool
        """
        async with self.semaphore:
            try:
                reader, writer = self.pool.pop()
            except IndexError:
                # empty list so create a new socket
                _log.info(f"Adding socket connection to device at {self.address}")
                reader, writer = await asyncio.open_connection(self.address, self.port)
            try:
                yield reader, writer
            finally:
                # put the socket back in the pool
                self.pool.append((reader, writer))
```

We can then test this out with a simple echo server that listens for connections and then takes some
time to respond.

```python

server code

```

And then a simple client to use it.

```python

client example in iPython

```
