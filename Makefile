install:
	poetry install

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	poetry run pip install dist/*.whl

lint:
	poetry run ruff check .

project:
	poetry run project

