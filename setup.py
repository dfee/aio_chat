from setuptools import setup, find_packages

setup(
    name='aio_chat',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'aiohttp ~= 2.0',
        'asphalt ~= 3.0',
        'asphalt-redis ~= 2.0',
        'asphalt-templating ~= 2.0',
        'asphalt-sqlalchemy ~= 3.0',
        'colorlog ~= 2.10',
        'Jinja2 >= 2.7.3',
        'inflection ~= 0.3',
        'ipython ~= 6.0',
        'psycopg2 ~= 2.7',
        'uvloop ~= 0.8',
    ],
    entry_points='''
    [console_scripts]
    road=aio_chat.scripts:road
    ''',
)
