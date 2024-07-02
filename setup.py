from setuptools import setup, find_packages

setup(
    name='canary_mission',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "pytest-playwright"
    ],
)
