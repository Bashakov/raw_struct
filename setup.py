from setuptools import setup, find_packages
from pkg_resources import parse_requirements


def load_requirements(fname):
    requirements = []
    for req in parse_requirements(open(fname, 'r').read()):
        extras = '[{}]'.format(','.join(req.extras)) if req.extras else ''
        requirements.append('{}{}{}'.format(req.name, extras, req.specifier))
    return requirements

setup(
    name='raw_struct',
    version='0.2',
    author='Andrey Bashakov',
    author_email='abashak@abisoft.spb.ru',
    url='https://github.com/Bashakov/raw_struct',
    packages=find_packages(exclude=['tests']),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    setup_requires=['pytest-runner'],
    install_requires=[],
    extras_require={'dev': load_requirements('requirements.dev.txt')}
)
