import os
from setuptools import setup, find_packages

# single source of truth for package version
version_ns = {}
with open(os.path.join("globus_cli", "version.py")) as f:
    exec(f.read(), version_ns)
version = version_ns['__version__']

setup(
    name="globus-cli",
    version=version,
    packages=find_packages(),
    install_requires=['globus-sdk'],

    entry_points={
        'console_scripts': ['globus = globus_cli:run_command']
    },

    # descriptive info, non-critical
    description="Globus CLI",
    long_description=open("README.md").read(),
    author="Stephen Rosen",
    author_email="sirosen@globus.org",
    url="https://github.com/globusonline/globus-cli",
    keywords=["globus", "cli", "command line"],
    classifiers=[
        "Development Status :: 5 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Programming Language :: Python"
    ],
)
