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
~/code/asphalt_sanic_demo on master via env [I] ➔ asphalt run development.yaml shell.yaml
INFO  2017-05-06 15:09:01,447 [sanic:724][MainThread] Goin' Fast @ http://0.0.0.0:9001
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

In [1]: async def notify(psm):
   ...:     print('Notify: "{}" on "{}" (from pattern "{}")'.format(
   ...:         psm.message,
   ...:         psm.channel,
   ...:         psm.pattern,
   ...:     ))
   ...:

In [2]: unsubscriber = call_async(pubsub.psubscribe, 'friend:*', notify)
INFO  2017-05-06 15:10:37,975 [asphalt_sanic_demo.pubsub.pubsub:115][MainThread] Subscribed to pattern: friend:*

In [3]: # Now, let's add our friends in the browser!

In [4]: INFO  2017-05-06 15:10:50,893 [asphalt_sanic_demo.pubsub.pubsub:88][MainThread] Sent messsage on friend:1: {"id": 1, "name": "tom"}
INFO  2017-05-06 15:10:50,894 [asphalt_sanic_demo.pubsub.pubsub:75][MainThread] Heard on channel friend:1: {"id": 1, "name": "tom"}
Notify: "{"id": 1, "name": "tom"}" on "friend:1" (from pattern "friend:*")
INFO  2017-05-06 15:10:54,590 [asphalt_sanic_demo.pubsub.pubsub:88][MainThread] Sent messsage on friend:2: {"id": 2, "name": "dick"}
INFO  2017-05-06 15:10:54,593 [asphalt_sanic_demo.pubsub.pubsub:75][MainThread] Heard on channel friend:2: {"id": 2, "name": "dick"}
Notify: "{"id": 2, "name": "dick"}" on "friend:2" (from pattern "friend:*")
INFO  2017-05-06 15:10:57,280 [asphalt_sanic_demo.pubsub.pubsub:88][MainThread] Sent messsage on friend:3: {"id": 3, "name": "harry"}
INFO  2017-05-06 15:10:57,281 [asphalt_sanic_demo.pubsub.pubsub:75][MainThread] Heard on channel friend:3: {"id": 3, "name": "harry"}
Notify: "{"id": 3, "name": "harry"}" on "friend:3" (from pattern "friend:*")
```
