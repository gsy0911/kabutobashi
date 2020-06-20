.PHONY: deploy
deploy: build
	twine upload dist/*

.PHONY: test-deploy
test-deploy: build
	twine upload -r testpypi dist/*

.PHONY: build
build: clean
	python setup.py sdist bdist_wheel

.PHONY: clean
clean:
	rm -f -r kabutobashi.egg-info/* dist/* -y

.PHONY: doc-build-sphinx
doc-build-sphinx: compile-python-docstring
	sphinx-build ./doc ./doc/_build

.PHONY: compile-python-docstring
compile-python-docstring:
	sphinx-apidoc -f -o ./doc ./kabutobashi