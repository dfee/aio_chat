from setuptools import setup, find_packages

setup(
    name='asphalt_sanic_demo',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'sanic ~= 0.5',
        'asphalt ~= 3.0',
        'asphalt-templating ~= 2.0',
        'asphalt ~= 3.0',
        'Jinja2 >= 2.7.3',
    ]
)
