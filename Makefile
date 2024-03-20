fmt:
	ruff format .

lint:
	ruff .

test:
	docker-compose -f docker-compose.test.yml up -d && pytest . -vv && docker-compose -f docker-compose.test.yml down

run:
	docker-compose -f docker-compose.yml up -d && uvicorn main:app --reload --port 8002