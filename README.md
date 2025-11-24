# Django Boilerplate

A modern Django REST API boilerplate with Docker support, Celery, Redis, PostgreSQL, and best practices.

## Features

- **Django 5.2+** with Python 3.13
- **Django REST Framework** for building APIs
- **PostgreSQL** database with optimized indexes
- **Redis** for caching and Celery broker
- **Celery** with Celery Beat for background tasks
- **Flower** for Celery monitoring
- **Docker & Docker Compose** for local and production environments
- **uv** package manager for fast dependency management
- **Ruff** for code formatting and linting
- **IPython** for enhanced Django shell
- **Custom User Model** with email authentication
- **JWT Authentication** with cookie-based support
- **AWS S3** for file storage
- **WhiteNoise** for static file serving
- **DRF Spectacular** for API documentation

## Project Structure

```
django-boilerplate/
├── config/                 # Django project configuration
│   ├── settings/          # Environment-specific settings
│   │   ├── base.py       # Base settings
│   │   ├── local.py      # Local development settings
│   │   └── deploy.py     # Production settings
│   ├── extensions/       # Celery configuration
│   └── urls.py          # Root URL configuration
├── users/                # Users app (example app structure)
│   ├── models/          # Models directory (not models.py)
│   │   ├── __init__.py
│   │   └── user.py
│   ├── migrations/
│   ├── admin.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── common/               # Shared utilities
├── utils/                # Utility functions
├── docker-compose.local.yaml
├── docker-compose.production.yaml
├── Dockerfile
├── pyproject.toml
└── manage.py
```

## App Structure Convention

**Important**: All apps should follow the `users` app structure:

- Use a `models/` directory instead of `models.py`
- Each model should be in its own file (e.g., `models/user.py`)
- Export models from `models/__init__.py`:
  ```python
  from .user import UserAccount
  
  __all__ = ["UserAccount"]
  ```

## Prerequisites

- Python 3.13
- **uv** package manager ([Installation](https://docs.astral.sh/uv/getting-started/installation/))
- Docker and Docker Compose (for containerized setup)
- PostgreSQL (if running locally without Docker)
- Redis (if running locally without Docker)

## Local Setup

### Option 1: Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django-boilerplate
   ```

2. **Create environment files**
   ```bash
   # Copy .env.example to .env
   cp .env.example .env
   
   # Copy db.env.example to db.env (for database configuration)
   cp db.env.example db.env
   ```

3. **Update `.env` file** with your configuration:
   ```env
   DJANGO_SECRET_KEY=your-secret-key-here
   DJANGO_DATABASE_NAME=your_db_name
   DJANGO_DATABASE_USER=your_db_user
   DJANGO_DATABASE_PASSWORD=your_db_password
   DJANGO_DATABASE_HOST=db
   DJANGO_DATABASE_PORT=5432
   CELERY_BROKER_URL=redis://redis:6379/0
   CELERY_RESULT_BACKEND=redis://redis:6379/0
   CELERY_FLOWER_USER=admin
   CELERY_FLOWER_PASSWORD=admin
   BACKEND_URL=http://localhost:8000
   AWS_STORAGE_BUCKET_NAME=your-bucket-name
   AWS_S3_REGION_NAME=us-east-1
   DEFAULT_FROM_EMAIL=Your App <noreply@yourapp.com>
   ```

4. **Update `db.env` file**:
   ```env
   POSTGRES_USER=your_db_user
   POSTGRES_PASSWORD=your_db_password
   POSTGRES_DB=your_db_name
   ```

5. **Build and start services**
   ```bash
   docker-compose -f docker-compose.local.yaml up --build
   ```

   This will start:
   - PostgreSQL database
   - Django backend (port 8000)
   - Redis
   - Celery worker
   - Celery beat
   - Flower (port 5555)

6. **Access the services**
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin
   - API Docs: http://localhost:8000/api/schema/swagger-ui/
   - Flower: http://localhost:5555

### Option 2: Local Development (Without Docker)

This project uses **uv** as the package manager for development.

1. **Clone and setup virtual environment**
   ```bash
   git clone <repository-url>
   cd django-boilerplate
   
   # Create virtual environment with uv
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies with uv**
   ```bash
   # Install all dependencies (including dev dependencies)
   uv sync
   
   # Or install only production dependencies
   uv sync --no-dev
   ```

3. **Create `.env` file**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

4. **Setup database**
   ```bash
   # Make sure PostgreSQL is running
   # Update DATABASE settings in .env
   
   # Run migrations
   uv run manage.py migrate
   ```

5. **Create superuser**
   ```bash
   uv run manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   uv run manage.py runserver
   ```

7. **Run Celery worker** (in a separate terminal)
   ```bash
   # Linux/Mac
   uv run celery -A config.extensions worker -l info -c 4 -Q emails
   
   # Windows (add --pool=threads)
   uv run celery -A config.extensions worker -l info -c 4 -Q emails --pool=threads
   ```
   
   Note: `emails` is the queue being used to send emails. Adjust the queue name (`-Q`) as needed for your queues.

8. **Run Celery beat** (in a separate terminal, optional)
   ```bash
   uv run celery -A config.extensions beat --loglevel=info
   ```

9. **Run Flower** (in a separate terminal, optional)
   ```bash
   uv run celery -A config.extensions flower
   ```
   
   Access Flower at http://localhost:5555

## Development Tools

### Package Management with uv

This project uses **[uv](https://docs.astral.sh/uv/)** as the package manager for fast and reliable dependency management.

**Common uv commands:**
```bash
# Install dependencies
uv sync

# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Remove a dependency
uv remove package-name

# Run commands in the virtual environment
uv run python manage.py <command>
uv run celery -A config.extensions worker
```

### Code Formatting and Linting with Ruff

This project uses **[Ruff](https://docs.astral.sh/ruff/)** for code formatting and linting.

**Format code:**
```bash
uv run ruff format .
```

**Check linting:**
```bash
uv run ruff check .
```

**Auto-fix linting issues:**
```bash
uv run ruff check --fix .
```

**Format and lint in one command:**
```bash
uv run ruff format . && uv run ruff check --fix .
```

Configuration is in `pyproject.toml`.

## Database Migrations

**Create migrations:**
```bash
uv run manage.py makemigrations
```

**Apply migrations:**
```bash
uv run manage.py migrate
```

**Show migration status:**
```bash
uv run manage.py showmigrations
```

**In Docker:**
```bash
docker-compose -f docker-compose.local.yaml exec backend python manage.py makemigrations
docker-compose -f docker-compose.local.yaml exec backend python manage.py migrate
```

## Creating a New App

When creating a new Django app, follow the `users` app structure:

1. **Create the app**
   ```bash
   uv run manage.py startapp myapp
   ```

2. **Create models directory structure**
   ```bash
   mkdir myapp/models
   touch myapp/models/__init__.py
   ```

3. **Create model files** (e.g., `myapp/models/my_model.py`)
   ```python
   from django.db import models
   
   class MyModel(models.Model):
       name = models.CharField(max_length=255)
       # ... other fields
       
       class Meta:
           indexes = [
               models.Index(fields=["name"], name="mymodel_name_idx"),
           ]
   ```

4. **Export from `models/__init__.py`**
   ```python
   """MyApp models"""
   
   from .my_model import MyModel
   
   __all__ = ["MyModel"]
   ```

5. **Register the app** in `config/settings/base.py`:
   ```python
   INTERNAL_APPS = [
       "users",
       "myapp",  # Add your app here
   ]
   ```

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `DJANGO_SECRET_KEY` - Django secret key
- `DJANGO_DATABASE_NAME` - PostgreSQL database name
- `DJANGO_DATABASE_USER` - PostgreSQL user
- `DJANGO_DATABASE_PASSWORD` - PostgreSQL password
- `DJANGO_DATABASE_HOST` - Database host
- `DJANGO_DATABASE_PORT` - Database port
- `CELERY_BROKER_URL` - Redis URL for Celery
- `CELERY_RESULT_BACKEND` - Redis URL for Celery results
- `CELERY_FLOWER_USER` - Flower admin username
- `CELERY_FLOWER_PASSWORD` - Flower admin password
- `BACKEND_URL` - Backend API URL
- `AWS_STORAGE_BUCKET_NAME` - S3 bucket name
- `AWS_S3_REGION_NAME` - AWS region
- `DEFAULT_FROM_EMAIL` - Default email sender

## API Documentation

API documentation is available at:
- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- ReDoc: http://localhost:8000/api/schema/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

## Testing

```bash
uv run manage.py test
```

## Production Deployment

See `docker-compose.production.yaml` for production configuration.

**Key differences:**
- Uses production settings (`config.settings.deploy`)
- Environment variables should be set securely
- SSL/TLS configuration
- Production database (RDS or managed PostgreSQL)

**Running with Gunicorn:**

For production deployment, the project uses Gunicorn with the production dependency group:

```bash
# Install production dependencies including gunicorn
uv sync --group production

# Run with gunicorn
uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

Or use the production group directly:
```bash
uv run --group production gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## Common Commands

All commands should be run with `uv run` to ensure they use the correct virtual environment:

```bash
# Create superuser
uv run manage.py createsuperuser

# Collect static files
uv run manage.py collectstatic --noinput

# Open Django shell (uses IPython)
uv run manage.py shell

# Check project
uv run manage.py check

# Show URLs
uv run manage.py showurls  # Requires django-extensions
```

## Running Celery and Flower

### Celery Worker

Run Celery worker to process background tasks:

```bash
# Linux/Mac
uv run celery -A config.extensions worker -l info -c 4 -Q emails

# Windows (add --pool=threads)
uv run celery -A config.extensions worker -l info -c 4 -Q emails --pool=threads
```

**Parameters:**
- `-l info` or `--loglevel=info`: Set log level to info
- `-c 4` or `--concurrency=4`: Number of worker processes/threads
- `-Q emails`: Queue name (adjust as needed for your queues)
- `--pool=threads`: Required on Windows (use `solo` or `threads` pool)

### Celery Beat

Run Celery beat for scheduled tasks:

```bash
uv run celery -A config.extensions beat --loglevel=info
```

### Flower

Run Flower for Celery monitoring:

```bash
uv run celery -A config.extensions flower
```

Access Flower at http://localhost:5555 (default port).

## Docker Commands

```bash
# Build images
docker-compose -f docker-compose.local.yaml build

# Start services
docker-compose -f docker-compose.local.yaml up

# Start in background
docker-compose -f docker-compose.local.yaml up -d

# Stop services
docker-compose -f docker-compose.local.yaml down

# View logs
docker-compose -f docker-compose.local.yaml logs -f backend

# Execute commands in container (shell uses IPython)
docker-compose -f docker-compose.local.yaml exec backend python manage.py shell
```

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

