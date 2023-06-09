.PHONY: tests

tests:
	python -m pytest tests

format:
	isort src
	black src

console:
	@textual console

debug:
	@textual run --dev tools/debug.py:Baca

publish:
	# poetry build
	poetry publish --build

typecheck:
	pyright src
