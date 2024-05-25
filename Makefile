fmt:
	ruff format .

sort:
	ruff check --select I --fix .
	
lint:
	ruff .

test:
	docker-compose -f docker-compose.test.yml down && docker-compose -f docker-compose.test.yml up -d && sleep 3 && pytest . -vv && docker-compose -f docker-compose.test.yml down

all:
	make fmt && make sort && make test

run:
	docker-compose down && docker-compose up -d && sleep 3 && uvicorn main:app --reload --port 8002

docker-test:
	docker-compose -f docker-compose.test.yml down && docker-compose -f docker-compose.test.yml up -d && sleep 2 
