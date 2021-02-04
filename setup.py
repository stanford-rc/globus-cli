import os

from setuptools import find_packages, setup

# single source of truth for package version
version_ns = {}  # type: ignore
with open(os.path.join("globus_cli", "version.py")) as f:
    exec(f.read(), version_ns)
version = version_ns["__version__"]

setup(
    name="globus-cli",
    version=version,
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.6",
    install_requires=[
        "globus-sdk==2.0.1",
        "click>=7.1.1,<8.0",
        "jmespath==0.10.0",
        "configobj>=5.0.6,<6.0.0",
        "requests>=2.0.0,<3.0.0",
        # cryptography has unusual versioning and compatibility rules:
        # https://cryptography.io/en/latest/api-stability/
        # we trust the two next major versions, per the Deprecation policy
        #
        # as new versions of cryptography are released, we may need to update
        # this requirement
        "cryptography>=1.8.1,<3.4.0",
    ],
    extras_require={
        # the development extra is for CLI developers only
        "development": [
            # testing
            "pytest<5",
            "pytest-cov<3.0",
            # mocking `requests`
            "responses==0.12.1",
            # loading fixture data
            "ruamel.yaml==0.16.12",
            # linting tools
            "black==20.8b1",
            "isort>=5.6.4,<6.0",
            "flake8>=3.8.4,<4.0",
            "flake8-bugbear==20.11.1",
            "mypy==0.800",
        ],
    },
    entry_points={"console_scripts": ["globus = globus_cli:main"]},
    # descriptive info, non-critical
    description="Globus CLI",
    long_description=open("README.rst").read(),
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
