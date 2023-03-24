# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='data-nft',
    version='0.1.0',
    description='MintScale Automotive Data NFT Library and Tooling',
    long_description=readme,
    author='MintScale Inc',
    author_email='admin@mintscale.io',
    url='https://github.com/mintscale/data-nft/',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
`
