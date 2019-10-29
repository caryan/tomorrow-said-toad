Title: Asyncio Socket Pool
Date: 2019-08-12
Modified: 2019-10-28
Category: Software
Tags: Python

In a typical client-server over a socket setup the server may take some time to process any given
request and so to allow thee client to fire off multiple requests in parallel to speed things up
there are two common paths:

1. We can make the server interface asynchronous so that it is able to take a whole series of
   requests and respond to them out of order.
2. The server can support multiple socket connections, but each one is
   blocking and so we can parallelize communications across the multiple sockets.

The first is more elegant but requires additional work to allow the server to asynchronously
dispatch requests and keep responding to new ones and for the client to handle the out of order
replies. We took that path with the [rpcq
client-server](https://github.com/rigetti/rpcq/tree/master/rpcq) For simpler cases, multiple sockets
might be sufficient.

Here is a simple implementation of a client socket pool wrapped an an [asynccontextmanager
decorator](https://docs.python.org/3/library/contextlib.html#contextlib.asynccontextmanager) so that
we can nicely `async with ...` `await` on the next available socket. To bound the number of sockets
we use an [asyncio
Semaphore](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore). The semaphore is
an integer that is intialized to the maximum number of sockets. Every time a socket is checked out
from the pool we `await` on the semphaore, the integer is decremented by one and then finally the
semaphore blocks when the integer would go negative. When we are done with the socket we return it
to the pool and increment the semaphore integer again. All this integer decrement/increment logic is
wrapped with by the Python `asyncio` module with another `asynccontextmanager` so all the
bookkeeping so the interface is a simple `async with self.semaphore:`. We'll return the high-level
`asyncio StreamReader/StreamWriter` to provide access to the socket.

```python
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, Tuple

class SocketPool():
    """
    A pool of socket connections for a client to access some server.
    """
    address: str
    """ Hostname for the server """

    port: int = 1234
    """ Port that the instrument is listening for connections on. """

    max_num_sockets: int = 10
    """ Maximum number of open sockets to the server """

    semaphore: asyncio.Semaphore
    """ Use a semaphore to bound the number of open connection to `max_num_sockets` """

    pool: list
    """ List of socket StreamReader, StreamWriter pairs """

    def __init__(self, address: str, max_num_sockets: Optional[int] = None, port: Optional[int] = None):
        self.address = address

        # if we're passed some `max_num_sockets` or `port` then override the defaults
        if max_num_sockets is not None:
            self.max_num_sockets = max_num_sockets

        if port is not None:
            self.port = port

        self.semaphore = asyncio.Semaphore(self.max_num_sockets)

        # a list to hold onto the (asyncio.StreamReader, asyncio.StreamWriter) tuples for each socket
        self.pool = []

    @asynccontextmanager
    async def get_socket(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """
        Get the next available socket reader/writer from the pool
        """
        async with self.semaphore:
            try:
                # take the last socket in the pool
                reader, writer = self.pool.pop()
            except IndexError:
                # empty list so create a new socket
                _log.info(f"Adding socket connection to server at {self.address}")
                reader, writer = await asyncio.open_connection(self.address, self.port)
            try:
                # hand the reader/writer pair back to the caller
                yield reader, writer
            finally:
                # put the socket back in the pool
                self.pool.append((reader, writer))
```

We can then test this out with a simple echo server that listens for connections and then takes some
time to respond.

```python

import asyncio

async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    print("Taking a second to process something....")
    await asyncio.sleep(1.0)

    print("Sending back response.")
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()

async def main():
    server = await asyncio.start_server(handle_echo, "localhost", 1234)

    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")

    async with server:
        await server.serve_forever()

asyncio.run(main())
```

And then a simple client side function to use it.

```python
import asyncio
from wherever.socket_pool import SocketPool

async def send_message(pool, msg):
    # check out a socket
    async with pool.get_socket() as (reader, writer):
        # send the message
        writer.write(msg.encode())
        await writer.drain()
        # wait for the echo response
        resp = await reader.read(100)
        return resp.decode()

pool = SocketPool("localhost" max_num_sockets=5)
```

```python
(base) cryan@cryan-Precision-5510:~/repos/tomorrow-said-toad/content$ ipython
Python 3.7.4 (default, Aug 13 2019, 20:35:49)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.8.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: %paste # import the client code
# send a single message and a single socket is created
In [2]: await send_message(pool, "Hello!")
Adding socket connection to server at localhost
Out[2]: 'Hello!'

# we can inspect the pool and see indeed there is one socket there
In [3]: pool.pool
Out[3]:
[(<StreamReader transport=<_SelectorSocketTransport fd=16 read=polling write=<idle, bufsize=0>>>,
  <StreamWriter transport=<_SelectorSocketTransport fd=16 read=polling write=<idle, bufsize=0>> reader=<StreamReader transport=<_SelectorSocketTransport fd=16 read=polling write=<idle, bufsize=0>>>>)]

In [4]: len(pool.pool)
Out[4]: 1

# now send a slew of requests at once and it still takes only a second to respond
In [5]: await asyncio.wait([send_message(pool, str(ct)) for ct in range(5)])
Adding socket connection to server at localhost
Adding socket connection to server at localhost
Adding socket connection to server at localhost
Adding socket connection to server at localhost
Out[5]:
({<Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='0'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='1'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='2'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='3'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='4'>},
 set())

# and we have 5 sockets in the pool
In [6]: len(pool.pool)
Out[6]: 5

# finally send even more requests and it takes about 4 seconds to respond as only 5 requests are outstanding at any time
In [7]: await asyncio.wait([send_message(pool, str(ct)) for ct in range(20)])
Out[7]:
({<Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='0'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='1'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='10'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='11'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='12'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='13'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='14'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='15'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='16'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='17'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='18'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='19'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='2'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='3'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='4'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='5'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='6'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='7'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='8'>,
  <Task finished coro=<send_message() done, defined at /home/cryan/repos/tomorrow-said-toad/content/client.py:61> result='9'>},
 set())

In [8]: len(pool.pool)
Out[8]: 5
```