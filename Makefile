tag:
	git tag "$(shell poetry version --short)"
	git push --tags

build:
	poetry build

publish-test: build
	poetry config repositories.testpypi https://test.pypi.org/legacy/
	poetry publish -r testpypi

publish: build
	poetry publish

release: tag publish
