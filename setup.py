from setuptools import setup

setup(
    name="globuscli",
    version="0.1.0",
    packages=["globuscli"],
    install_requires=['globus-sdk-python'],
    # for now, install directly from GitHub
    # TODO: once this is on pypi, install from there
    dependency_links=[
        'https://github.com/globusonline/globus-sdk-python/archive/support-globus-cli.zip#egg=globus-sdk-python-0.1'
    ],

    # descriptive info, non-critical
    description="Globus CLI",
    long_description=open("README.md").read(),
    author="Stephen Rosen",
    author_email="sirosen@globus.org",
    url="https://github.com/globusonline/globus-cli",
    keywords=["globus", "cli", "command line"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
    ],
)
