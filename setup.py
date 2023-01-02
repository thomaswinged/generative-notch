from setuptools import setup, find_packages


with open('requirements.txt') as file:
    req = file.read().split()

setup(
    name='generative_notch',
    description='Generating probabilistically trait-driven art using Notch and StableDiffusion',
    version='0.2.0',
    author='Thomas Winged',
    install_requires=req,
    packages=find_packages()
)
