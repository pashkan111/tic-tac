fmt:
	ruff format .

lint:
	ruff .

test:
	docker-compose up -d && pytest . -vv
