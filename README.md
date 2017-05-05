# asphalt_sanic_demo
This demonstrates a very simple application that uses `sanic` as a webserver,
and `jinja2` as the template engine ... within the `asphalt` framework.

## Instructions

### Create database
Assuming you have PostgreSQL installed, issue this command:
    `createdb asphalt_sanic_demo`

### Serve
1. create a virtual environment:
    `python -m venv env`

2. activate virtual environment:
   `src env/bin/activate`

3. install package:
   `pip install -e .`

4. run asphalt:
   `asphalt run development.yaml`

5. in your browser, visit:
    `http://localhost:9000`

### Shell
Simply call `asphalt run development.yaml shell.yaml`. Note that the `sanic`
application is actively running in the background (as well as `aioredis`). This
means that if you want to have a CLI interface and a web interface at the same
time, you've got it! Practically, other services might be helpful - like access
to redis.

If you'd like to run coroutines on the loop, simply:
    `call_async(my_coroutine, arg1, arg2)`

For example, here's setting and getting a Redis value:
```
Python 3.6.0 (default, Mar  6 2017, 17:37:38)
Type 'copyright', 'credits' or 'license' for more information
IPython 6.0.0 -- An enhanced Interactive Python. Type '?' for help.

Environment:
        ctx             asphalt.core.context
        loop            asyncio.unix_events
        call_async      asphalt.core.context
        redis           aioredis.commands
        jinja2          asphalt.templating.api
        server          sanic.app
        sql             sqlalchemy.orm.session

In [1]: call_async(redis.set, 'my_key', 'my_value')
Out[1]: True

In [2]: call_async(redis.get, 'my_key')
Out[2]: b'my_value'
```
