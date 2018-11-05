VIRTUALENV=.venv
CLI_VERSION=$(shell grep '^__version__' globus_cli/version.py | cut -d '"' -f2)

.PHONY: build release localdev test clean showvars help travis

help:
	@echo "These are our make targets and what they do."
	@echo "All unlisted targets are internal."
	@echo ""
	@echo "  help:      Show this helptext"
	@echo "  showvars:  Show makefile variables"
	@echo "  localdev:  Setup local development env with a 'setup.py develop'"
	@echo "  build:     Create the source distributions for release"
	@echo "  test:      Run the full suite of tests"
	@echo "  release:   [build], but also upload to pypi using twine and create a signed git tag"
	@echo "  clean:     Remove typically unwanted files, mostly from [build]"


showvars:
	@echo "CLI_VERSION=$(CLI_VERSION)"


$(VIRTUALENV):
	virtualenv $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install --upgrade pip
	$(VIRTUALENV)/bin/pip install --upgrade setuptools


localdev: $(VIRTUALENV)
	$(VIRTUALENV)/bin/python setup.py develop


build: $(VIRTUALENV)
	rm -rf dist/
	$(VIRTUALENV)/bin/python setup.py sdist bdist_egg


$(VIRTUALENV)/bin/twine: $(VIRTUALENV) upload-requirements.txt
	$(VIRTUALENV)/bin/pip install -U -r upload-requirements.txt

release: $(VIRTUALENV)/bin/twine build
	$(VIRTUALENV)/bin/twine upload dist/*
	git tag -s "$(CLI_VERSION)" -m "v$(CLI_VERSION)"

$(VIRTUALENV)/bin/flake8 $(VIRTUALENV)/bin/nose2: test-requirements.txt $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install -r test-requirements.txt
	touch $(VIRTUALENV)/bin/flake8
	touch $(VIRTUALENV)/bin/nose2

test: $(VIRTUALENV)/bin/flake8 $(VIRTUALENV)/bin/nose2 localdev
	$(VIRTUALENV)/bin/flake8
	$(VIRTUALENV)/bin/nose2 --verbose


travis:
	pip install --upgrade pip
	pip install --upgrade "setuptools>=29"
	pip install -r test-requirements.txt
ifeq (, $(findstring pypy, $(TRAVIS_PYTHON_VERSION)))
	pip install "cryptography>=1.8.1,<2.0.0"
endif
	python setup.py develop
	flake8
	nose2 --verbose


clean:
	-rm -r $(VIRTUALENV)
	-rm -r dist
	-rm -r build
	-rm -r *.egg-info
	find . -name '*.pyc' -delete
