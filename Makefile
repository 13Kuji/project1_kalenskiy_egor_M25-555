install:
	poetry install

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	poetry run pip install dist/*.whl

project:
	poetry run project

