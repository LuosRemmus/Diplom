flake:
	poetry run flake8 \
		--per-file-ignores="__init__.py:F401" \
		--ignore E203,E501,W503,PIE803,PIE786,DUO104,DUO110 \
		backend

format:
	@echo "Форматирование"
	poetry run isort .
	poetry run black .
