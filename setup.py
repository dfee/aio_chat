from setuptools import setup, find_packages

setup(
    name='asphalt_sanic_demo',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'asphalt ~= 3.0',
        'asphalt-redis ~= 2.0',
        'asphalt-templating ~= 2.0',
        'asphalt-sqlalchemy ~= 3.0',
        'colorlog ~= 2.10',
        'Jinja2 >= 2.7.3',
        'ipython ~= 6.0',
        'psycopg2 ~= 2.7',
        'sanic ~= 0.5',
    ],
)
