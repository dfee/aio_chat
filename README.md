# asphalt_sanic_demo
This demonstrates a very simple application that uses `sanic` as a webserver,
and `jinja2` as the template engine ... within the `asphalt` framework.

## Instructions

### Serve
1. create a virtual environment:
    `python -m venv env`

2. activate virtual environment:
   `src env/bin/activate`

3. install package:
   `pip install -e .`

4. run asphalt:
   `asphalt run config.yaml`

### Shell
Simply call `ash config.yaml`. Note that the `sanic` application is actively
running in the background (as well as `aioredis`). This means that if you
want to have a CLI interface and a web interface at the same time, you've got
it! Practically, other services might be helpful - like access to redis.

If you'd like to run coroutines on the loop, simply:
    `run_on_loop(my_coroutine(arg1, arg2))`

For example, here's setting and getting a Redis value:
```
Python 3.6.0 (default, Mar  6 2017, 17:37:38)
Type 'copyright', 'credits' or 'license' for more information
IPython 6.0.0 -- An enhanced Interactive Python. Type '?' for help.

Environment:
        loop            asyncio.unix_events
        run_on_loop     __main__
        redis           aioredis.commands
        jinja2          asphalt.templating.api
        server          sanic.app

In [1]: fut = run_on_loop(redis.set('asdf', 1234))

In [2]: fut.result()
Out[2]: True

In [3]: fut2 = run_on_loop(redis.get('asdf'))

In [4]: fut2.result()
Out[4]: b'1234'
```
