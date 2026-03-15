create-venv:
	python -m venv .webscraping
	@echo "✓ Ambiente virtual creado, recuerda activarlo: source .webscraping/bin/activate "


install:
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✓ Dependencias instaladas "


run-scraping:
	python src/main.py