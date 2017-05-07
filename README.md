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


### Shell
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


### Complex Example
You can explore all these techniques by running by following this more complex
messsaging example. In this example we'll run the server on `localhost:9000`
and `localhost:9001`. As we send messages through each website, the other
website will receive the input through the PubSub resource (which in turn relies
on the redis resource), and upon reloading the page, we'll see all the previous
messages as they've been persisted using our sqlalchemy resource, rendered
using our templating resource.

1. in one terminal run (note, this will run on port 9000 by default):
```
asphalt run development.yaml
```

2. in a second terminal run (note, this will run on port 9001 by default):
```
asphalt run development.yaml shell.yaml
```

3. open up two browser windows to `localhost:9000` and `localhost:9001`
respectively.

4. send a message in either browser window, and watch the message be passed
to the other window.

5. reload the page to see that the messages have been persistenly stored.
