from setuptools import setup

setup(
    name='vpmbench',
    version='0.0.1',
    packages=['tests', 'vpmbench'],
    url='',
    license='MIT',
    author='Andreas Ruscheinski',
    author_email='andreas.ruscheinski@uni-rostock.de',
    description='',

    install_requires=[
        "pandas>=1.2.1",
        "pandera>=0.6.2",
        "pyyaml>=5.4.1",
        "docker>=4.4.2",
        "scikit-learn>=0.24.1",
        "numpy>=1.19.4",
        "matplotlib>=3.3.4",
        "vcfpy==0.13.3",
        "pysam==0.17.0"
    ],
    extras_require={
        "dev": ["pytest>=6.2.1",
                "sphinx>=3.4.0",
                "sphinx-rtd-theme>=0.5.0",
                "tox>=3.22.0"]
    }
)
