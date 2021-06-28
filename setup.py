import os
import re

from setuptools import find_packages, setup

DEV_REQUIREMENTS = [
    # lint
    "flake8<4",
    "isort<6",
    "black==21.5b1",
    "flake8-bugbear==21.4.3",
    "mypy==0.812",
    # tests
    "pytest<7",
    "pytest-cov<3",
    "pytest-xdist<3",
    "responses==0.13.3",
    # loading test fixture data
    "ruamel.yaml==0.16.12",
]


def parse_version():
    # single source of truth for package version
    version_string = ""
    version_pattern = re.compile(r'__version__ = "([^"]*)"')
    with open(os.path.join("src", "globus_cli", "version.py")) as f:
        for line in f:
            match = version_pattern.match(line)
            if match:
                version_string = match.group(1)
                break
    if not version_string:
        raise RuntimeError("Failed to parse version information")
    return version_string


def read_readme():
    with open("README.rst") as fp:
        return fp.read()


setup(
    name="globus-cli",
    version=parse_version(),
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    install_requires=[
        "globus-sdk==3.0.0a4",
        "click>=7.1.1,<8.0",
        "jmespath==0.10.0",
        "requests>=2.0.0,<3.0.0",
        # cryptography has unusual versioning and compatibility rules:
        # https://cryptography.io/en/latest/api-stability/
        # we trust the two next major versions, per the Deprecation policy
        #
        # as new versions of cryptography are released, we may need to update
        # this requirement
        "cryptography>=1.8.1,<3.4.0",
    ],
    extras_require={"development": DEV_REQUIREMENTS},
    entry_points={"console_scripts": ["globus = globus_cli:main"]},
    # descriptive info, non-critical
    description="Globus CLI",
    long_description=read_readme(),
    author="Stephen Rosen",
    author_email="sirosen@globus.org",
    url="https://github.com/globus/globus-cli",
    keywords=["globus", "cli", "command line"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
