# Dependencies

## Python

- `requests` - HTTP library used to fetch data from external sources including the archive JSON feed
- `flask-caching` - allows the caching of routes and time-intensive functions
- `tna-frontend-jinja` - Jinja2 templates for TNA Frontend components
- `flask-talisman` - adds configuration for better security including [CSP](https://nationalarchives.github.io/engineering-handbook/technology/standards/security/#csp)
- `sentry-sdk` - sends Python errors to the Sentry dashboard for monitoring
- `pydash` - library of Python utilities to make object querying and manipulation easier
- `redis` - Redis client used as the cache backend in production and staging environments
- `beautifulsoup4` - parses and transforms HTML from Wagtail rich text fields, e.g. adding CSS classes and sanitising attributes
- `sqlalchemy` - ORM and database toolkit used to manage and query the local archive records database
- `alembic` - database migration tool used alongside SQLAlchemy to manage schema changes
- `pydantic` - data validation library used to validate and parse the archive JSON feed before saving to the database
