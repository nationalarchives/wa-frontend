# UK Web Archive Frontend

## UKGWA Local Repository Setup

This guide covers setting up both the backend (ds-wagtail) and frontend (wa-frontend) repositories for local development.

### Backend - ds-wagtail

1. Clone the repo locally:
   ```sh
   git clone git@github.com:nationalarchives/ds-wagtail.git
   ```

2. Within the project folder, rename the example env file `cp .env.example .env`, its not used for anything by us but the build checks for its existence

3. In the root directory of the project create a new `docker-compose.override.yml` file, and add the following content:
   ```yaml
   services:
     app:
       environment:
         - WAGTAILAPI_BASE_URL=http://host.docker.internal:8000
         - WAGTAILAPI_IMAGES_BASE_URL=http://localhost:8000
         - WAGTAILAPI_MEDIA_BASE_URL=http://localhost:8000
   ```

4. Build the container:
   ```sh
   docker compose up --build -d
   ```

5. Run migrations:
   ```sh
   docker compose exec app poetry run python manage.py migrate
   ```

6. Create a superuser:
   ```sh
   docker compose exec app python manage.py createsuperuser
   ```

7. Log in to the wagtail admin site (should be http://localhost:8000/admin)

8. Create a new page at the root of type "UKGWA Home Page", this will be our new sites homepage

9. Create a new site (Settings > Sites):
   - Hostname: `localhost`
   - Port: `65500`
   - Site Name: `UK Gov Web Archive`
   - Home page: The page created in step 8.

10. Check the page is displayed when querying the site-specific page endpoint and its detail view can be accessed:
    - http://localhost:8000/api/v2/pages/?site=localhost:65500
    - http://localhost:8000/api/v2/pages/{PAGE_ID}/?site=localhost:65500

### Frontend - wa-frontend

1. Clone the repo locally:
   ```sh
   git clone git@github.com:nationalarchives/ds-wagtail.git
   ```

2. In the root directory of the project create a new `docker-compose.override.yml` file, and add the following content:
   ```yaml
   services:
     app:
       environment:
         - WAGTAIL_SITE_HOSTNAME=localhost:65500
   ```

3. Within the project folder build the container:
   ```sh
   docker compose up --build -d
   ```

4. Visit http://localhost:65500/ to view the frontend site

## Quickstart

```sh
# Build and start the container
docker compose up -d
```

### Add the static assets

During the first time install, your `app/static/assets` directory will be empty.

As you mount the project directory to the `/app` volume, the static assets from TNA Frontend installed inside the container will be "overwritten" by your empty directory.

To add back in the static assets, run:

```sh
docker compose exec app cp -r /app/node_modules/@nationalarchives/frontend/nationalarchives/assets /app/app/static
```

### Run tests

```sh
docker compose exec app poetry run python -m pytest
```

### Format and lint code

```sh
docker compose exec app format
```

## Environment variables

In addition to the [base Docker image variables](https://github.com/nationalarchives/docker/blob/main/docker/tna-python/README.md#environment-variables), this application has support for:

| Variable                         | Purpose                                                                     | Default                                                   |
| -------------------------------- | --------------------------------------------------------------------------- | --------------------------------------------------------- |
| `CONFIG`                         | The configuration to use                                                    | `config.Production`                                       |
| `DEBUG`                          | If true, allow debugging[^1]                                                | `False`                                                   |
| `COOKIE_DOMAIN`                  | The domain to save cookie preferences against                               | _none_                                                    |
| `CSP_IMG_SRC`                    | A comma separated list of CSP rules for `img-src`                           | `'self'`                                                  |
| `CSP_SCRIPT_SRC`                 | A comma separated list of CSP rules for `script-src`                        | `'self'`                                                  |
| `CSP_STYLE_SRC`                  | A comma separated list of CSP rules for `style-src`                         | `'self'`                                                  |
| `CSP_FONT_SRC`                   | A comma separated list of CSP rules for `font-src`                          | `'self'`                                                  |
| `CSP_CONNECT_SRC`                | A comma separated list of CSP rules for `connect-src`                       | `'self'`                                                  |
| `CSP_MEDIA_SRC`                  | A comma separated list of CSP rules for `media-src`                         | `'self'`                                                  |
| `CSP_WORKER_SRC`                 | A comma separated list of CSP rules for `worker-src`                        | `'self'`                                                  |
| `CSP_FRAME_SRC`                  | A comma separated list of CSP rules for `frame-src`                         | `'self'`                                                  |
| `CSP_FRAME_ANCESTORS`            | A comma separated list of CSP rules for `frame-accestors`                   | `'self'`                                                  |
| `CSP_FEATURE_FULLSCREEN`         | A comma separated list of rules for the `fullscreen` feature policy         | `'self'`                                                  |
| `CSP_FEATURE_PICTURE_IN_PICTURE` | A comma separated list of rules for the `picture-in-picture` feature policy | `'self'`                                                  |
| `CSP_REPORT_URL`                 | The URL to report CSP violations to                                         | _none_                                                    |
| `FORCE_HTTPS`                    | Redirect requests to HTTPS as part of the CSP                               | _none_                                                    |
| `CACHE_TYPE`                     | https://flask-caching.readthedocs.io/en/latest/#configuring-flask-caching   | _none_                                                    |
| `CACHE_DEFAULT_TIMEOUT`          | The number of seconds to cache pages for                                    | production: `300`, staging: `60`, develop: `0`, test: `0` |
| `CACHE_DIR`                      | Directory for storing cached responses when using `FileSystemCache`         | `/tmp`                                                    |
| `GA4_ID`                         | The Google Analytics 4 ID                                                   | _none_                                                    |

[^1] [Debugging in Flask](https://flask.palletsprojects.com/en/2.3.x/debugging/)
