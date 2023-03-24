.PHONY: tests

tests:
	python -m pytest tests

format:
	isort src
	black src
