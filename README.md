# asphalt_sanic_demo
This demonstrates a very simple application that uses the following components
running within the `asphalt` framework:
* jinja2 (`asphalt_templating`)
* sqlalchemy (`asphalt_sqlalchemy`)
* redis (`asphalt_redis`)
* sanic (custom)
* pubsub (custom)

The purpose of this demo is to show a very basic Create / Retrieve web
application, where the data is persistently stored in a Postgres database,
and the additions are published to a Redis pubsub channel.

## Instructions

### Create database
Assuming you have PostgreSQL installed, issue this command:
```
createdb asphalt_sanic_demo
```


### Install
1. create a virtual environment:
```
python -m venv env
```

2. activate virtual environment:
```
src env/bin/activate
```

3. install package:
```
pip install -e .
```


### Update configuration
Sane defaults are assumed by the development config, but you can update them
accordingly.
```
asphalt_sanic_demo/development.yaml
```


### Serve
Execute the following command:
```
asphalt run development.yaml
```
Now, in your browser visit `http://localhost:9000`.


### Explore
Simply call `asphalt run development.yaml shell.yaml`. Note that the `sanic`
(and all services) are actively running in the background. This means that if
you want to have a CLI interface and a web interface at the same time, you've
got it! Practically, other services might be helpful - like access to redis.

If you'd like to run coroutines on the loop, use this format:
```
call_async(my_coroutine, arg1, arg2)
```

For example, to run the server and a shell, run this command:
```
asphalt run development.yaml shell.yaml
```
And visit `http://localhost:9001` in your browser.

Now, follow this tutorial:

```
~/code/asphalt_sanic_demo on master [!?] via env [I] ➔ asphalt run development.yaml shell.yaml
INFO  2017-05-06 02:50:32,954 [sanic:724][MainThread] Goin' Fast @ http://0.0.0.0:9001
Python 3.6.0 (default, Mar  6 2017, 17:37:38)
Type 'copyright', 'credits' or 'license' for more information
IPython 6.0.0 -- An enhanced Interactive Python. Type '?' for help.

Environment:
        ctx             asphalt.core.context
        call_async      asphalt.core.context
        loop            asyncio.unix_events
        jinja2          asphalt.templating.api
        pubsub          asphalt_sanic_demo.pubsub.pubsub
        redis           aioredis.commands
        server          sanic.app
        sql             sqlalchemy.orm.session

In [1]: async def notifier(message):
   ...:     print(message)
   ...:

In [2]: unsubscriber = call_async(pubsub.psubscribe, 'friend:*', notifier)
INFO  2017-05-06 02:50:54,172 [asphalt_sanic_demo.pubsub.pubsub:83][MainThread] Subscribed to pattern: friend:*

In [3]: # Now, let's add our friends in the browser!

In [4]: INFO  2017-05-06 02:51:08,473 [asphalt_sanic_demo.pubsub.pubsub:52][MainThread] Sent messsage on friend:13: {"id": 1, "name": "bill"}
INFO  2017-05-06 02:51:10,825 [asphalt_sanic_demo.pubsub.pubsub:52][MainThread] Sent messsage on friend:14: {"id": 2, "name": "susan"}
INFO  2017-05-06 02:51:13,197 [asphalt_sanic_demo.pubsub.pubsub:52][MainThread] Sent messsage on friend:15: {"id": 3, "name": "jack"}
```
