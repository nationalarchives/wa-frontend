# WA Frontend

## Start the containers

```sh
docker compose up -d
```

## Run the tests

```sh
docker compose exec app poetry run python -m pytest
```

## Format the code

```sh
docker compose exec app format
```

## Upgrade dependencies

```sh
docker compose exec app upgrade
```
