from setuptools import setup, find_packages
from pathlib import Path


setup(
    name='raw_struct',
    version='0.1',
    author='Andrey Bashakov',
    author_email='abashak@abisoft.spb.ru',
    packages=find_packages(exclude=['tests']),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
)
