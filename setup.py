from setuptools import setup, find_packages

setup(
    name="globuscli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=['globus-sdk-python'],
    # for now, install directly from GitHub
    # TODO: once this is on pypi, install from there
    dependency_links=[
        ('https://github.com/globusonline/globus-sdk-python/'
         'archive/master.zip#egg=globus-sdk-python-0.1')
    ],

    entry_points={
        'console_scripts': ['globuscli = globuscli.parse_cmd:run_command']
    },

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
