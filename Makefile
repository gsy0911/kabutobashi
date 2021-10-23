.PHONY: help
help: ## show commands ## make
	@printf "\033[36m%-30s\033[0m %-50s %s\n" "[Sub command]" "[Description]" "[Example]"
	@grep -E '^[/a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | perl -pe 's%^([/a-zA-Z_-]+):.*?(##)%$$1 $$2%' | awk -F " *?## *?" '{printf "\033[36m%-30s\033[0m %-50s %s\n", $$1, $$2, $$3}'


.PHONY: format
format: ## format with black ## make format
	black kabutobashi --line-length 120
	black test --line-length 120

.PHONY: deploy
deploy: ## upload to pypi ## make deploy
	twine upload dist/*

.PHONY: test-deploy
test-deploy: ## upload to test-pypi ## make test-deploy
	twine upload -r testpypi dist/*

.PHONY: build
build: clean ## create wheel ## make build
	python setup.py sdist bdist_wheel

.PHONY: clean
clean: ## clean the wheel directory ## make clean
	rm -f -r kabutobashi.egg-info/* dist/* -y

.PHONY: test-python
test-python: ## execute test with pytest ## make test-python
	pytest ./test -vv --cov=./kabutobashi --cov-report=html
