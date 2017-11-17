from setuptools import setup


with open('README.md') as f:
    DESCRIPTION = f.read()


setup(
    name='specparse',
    version='0.1',
    license='MIT',
    long_description=DESCRIPTION,
    packages=['specparse'],
    scripts=['scripts/print-spec'],
    install_requires=['argparse', 'yaml']
)
