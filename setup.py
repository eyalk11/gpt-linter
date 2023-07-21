from setuptools import setup
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
import pkg_resources
import setuptools
import pathlib
desc = 'Python minor issue resolver (mypy) using gpt by openai! '
with pathlib.Path('requirements.txt').open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]

setup(
    name='mypy-gpt',
    version='1.0.1',
    packages=['mypy_gpt'],
    url='https://github.com/eyalk11/mypy-gpt',
    license=' AGPL-3.0 license',
    author='ekarni',
    author_email='',
    description=desc,
    long_description=desc,
    install_requires=install_requires
)
