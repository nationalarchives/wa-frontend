# Structure

## `app`

The application code.

### `app/api`

The internal REST API blueprint exposing archive data endpoints. Used for A-Z progressing enhancements.

- `GET /api/archive/characters` - returns available A-Z characters from the local database
- `GET /api/archive/records?character=X` - returns archive records for a given character

### `app/healthcheck`

The health check endpoint.

### `app/lib`

This contains reusable functionality that can be used throughout the site. Notable files are:

- `app/lib/api.py` - a generic JSON API client for Wagtail requests
- `app/lib/archive_service.py` - cached database queries for archive record data
- `app/lib/cache.py` - the cache configuration
- `app/lib/content_parser.py` - functions to mutate content from Wagtail and transform it into TNA Frontend compliant code
- `app/lib/context_processor.py` - functions that can be used inside Jinja2 templates
- `app/lib/database.py` - SQLAlchemy database setup and session management
- `app/lib/models.py` - ORM model definitions (e.g. `ArchiveRecord`)
- `app/lib/navigation.py` - utilities for building header and footer navigation
- `app/lib/pagination.py` - create objects suitable for the pagination component in TNA Frontend
- `app/lib/query.py` - query string utilities
- `app/lib/schemas.py` - Pydantic schemas for validating the archive JSON feed
- `app/lib/talisman.py` - the reusable Talisman module for configuring security throughout the site
- `app/lib/template_filters.py` - filters that can be used in Jinja2 templates
- `app/lib/util.py` - replicates the `strtobool` function removed from Python 3.11

### `app/main`

The main routes for the site, including the home page and cookies page.

### `app/sitemaps`

Routes for creating the [XML sitemap](http://localhost:65497/sitemap.xml) and all the sub-sitemaps, e.g. [/sitemaps/sitemap_1.xml](http://localhost:65497/sitemaps/sitemap_1.xml), [/sitemaps/sitemap_2.xml](http://localhost:65497/sitemaps/sitemap_2.xml).

`/sitemap.xml` is the entrypoint sitemap that links to the other sitemaps.

`/sitemaps/sitemap_1.xml` is the sitemap that covers static routes defined in this service.

`/sitemaps/sitemap_2.xml` and onwards are dynamic pages defined in Wagtail.

The templates for these routes can be found in `app/templates/sitemaps`.

### `app/static`

This is largely ignored by version control as most of the static assets are compiled or copied in as part of the [`tna-build`](https://github.com/nationalarchives/docker/tree/main/docker/tna-python#tna-build) process in the `Dockerfile`.

Any static images that are needed for this site can be placed in `app/static/images` (which is not ignored by version control) and included in the HTML using the `url_for` function:

```html
<img
  src="{{ url_for('static', filename='images/example.svg') }}"
  width="128"
  height="128"
  alt=""
/>
```

Avoid adding large images and binary files to this repository. Try to use SVGs where possible.

### `app/templates`

Jinja2 templates for the site.

Notable directories are:

- `app/templates/components` - duplicates of [TNA Frontend Jinja](https://github.com/nationalarchives/tna-frontend-jinja) templates which will override the default templates
- `app/templates/errors` - error pages such as 404 and 500 responses
- `app/templates/layouts` - generic, reusable page layouts
- `app/templates/macros` - reusable macros, including blocks used to render Wagtail streamfield content
- `app/templates/main` - page templates for the home page and cookies page
- `app/templates/pages` - content page templates including the A-to-Z archive index and listing pages

### `app/wagtail`

Includes the routing for Wagtail pages and an API (`api.py`) to get content from Wagtail.

The routing will call `render_content_page` in `render.py` and depending on the page type returned from Wagtail (defined in `page_type_templates`) will load the appropriate page renderer from `app/wagtail/pages`.

### `app/commands.py`

Flask CLI commands for managing archive data:

- `flask sync-archive-data` - fetches the archive JSON feed and syncs records to the local database
- `flask clear-archive-cache` - clears the archive data cache without running a full sync

## `src`

The source files for CSS and JavaScript.

### `src/scripts`

The JavaScript files to be compiled at build time.

Each file requiring compilation needs to be included in `webpack.config.js`.

JavaScript files get compiled to `app/static` and can be used in templates with:

```html
{% block bodyEnd %} {{ super() }}
<script
  src="{{ url_for('static', filename='my-js-file.min.js', v=app_config.BUILD_VERSION) }}"
  defer
></script>
{% endblock %}
```

### `src/styles`

The SCSS files to be compiled to CSS at build time.

All SCSS files in this directory will be compiled to `app/static`. To exclude files from being compiled (such as modules for includes), prefix the files with an underscore (e.g. `src/styles/main/_generics.scss`).

These CSS files can be used in templates with:

```html
{% block stylesheets %} {{ super() }}
<link
  rel="stylesheet"
  href="{{ url_for('static', filename='my-css-file.css', v=app_config.BUILD_VERSION) }}"
  media="screen,print"
/>
{% endblock %}
```

## `migrations`

Database migration files managed by Alembic. Run migrations with:

```sh
flask db upgrade
```

## `test`

Test files which should closely match the directory structure of the `app` directory.

## `config.py`

A file containing configuration for `Production`, `Staging`, `Develop` and `Test`.

Define default values in `Production` and overwrite them only in the configurations that need it.

This is the application configuration and not the [container environment](https://github.com/nationalarchives/docker/tree/main/docker/tna-python#environment-variables) which affects how the code is run (number of threads/workers etc.).

## `docker-compose.yml`

This is only used for local development. Configuration added and edited here will not affect production builds.

Don't put secrets in here (e.g. API keys) - add these to a local `docker-compose.override.yml` file instead.

## `Dockerfile`

The file that will be used to build images in GitHub Actions.

Keep this file as terse as possible.

## `main.py`

The entrypoint for the application as defined in the `CMD` on the [`Dockerfile`](#dockerfile).
