# Django Site Settings

[![PyPI version](https://img.shields.io/pypi/v/django-site-settings.svg)](https://pypi.org/project/django-site-settings/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-site-settings.svg)](https://pypi.org/project/django-site-settings/)
[![Django Versions](https://img.shields.io/pypi/djversions/django-site-settings.svg)](https://pypi.org/project/django-site-settings/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Django Site Settings** is a reusable Django application designed to manage dynamic, type-safe global configurations directly from the Django Admin panel. Built on top of `django-solo`, it guarantees a singleton pattern for your core settings while offering an advanced, customizable caching layer.

---

## Features

* **Singleton Architecture**: Ensures only one global configuration instance exists.
* **Strict Type Validation**: Supports **String**, **Integer**, **Float**, and **Boolean** data types with strict validation on save.
* **High-Performance Caching**: Automatically caches values to minimize database hits.
* **Multi-Cache Support**: Seamlessly integrates with your existing cache infrastructure (Redis, Memcached, etc.).
* **Smart Cache Invalidation**: Uses Django signals to instantly purge modified or deleted keys.
* **Template Tag Ready**: Built-in template tags to fetch settings directly inside your HTML layouts.

---

## Requirements

* **Python**: 3.10, 3.11, 3.12+
* **Django**: 5.0, 6.0+
* **django-solo**: 2.3.0+

---

## Installation

### Via pip
```bash
pip install django-site-settings
```

### Via Poetry
To add the package as a dependency using Poetry, run the following command:

```bash
poetry add django-site-settings
```


## Configuration
1. Add solo and django_site_settings to your project's INSTALLED_APPS inside settings.py:

```python
INSTALLED_APPS = [
    # ... Django core apps
    
    "solo",
    "django_site_settings",
    
    # ... Your local apps
]
```

2. Run the database migrations:

```bash
python manage.py migrate
```

## Advanced Customization (Optional)
You can customize the caching behavior by adding the following variables to your main Django settings.py:

```python
# Cache TTL in seconds (Default is 7 days)
SITE_SETTINGS_CACHE_TIMEOUT = 86400  # 24 hours

# Specify which cache backend configuration from your CACHES setting to use (Default is "default")
SITE_SETTINGS_CACHE_ALIAS = "fast_redis"
```

## Usage
### Fetching Settings in Python Code 
Use the get_setting utility function anywhere in your Python business logic (services, models, tasks, or utilities) with automatic type conversion:

```python
from django_site_settings.utils import get_setting

# Safely pulls from cache with strict type conversion
max_attempts = get_setting("MAX_LOGIN_ATTEMPTS", default=3)
is_maintenance = get_setting("MAINTENANCE_MODE", default=False)
api_timeout = get_setting("EXTERNAL_API_TIMEOUT", default=5.0)

if is_maintenance:
    # Handle maintenance logic directly
    pass
```

### Fetching Settings inside Django Templates
Load the custom template tags to output values natively inside your HTML files:

```html
{% load site_settings_tags %}

<footer>
    <p>Contact Support: {% site_setting "SUPPORT_EMAIL" default="support@example.com" %}</p>
    
    {% site_setting "SHOW_PROMO_BANNER" default=False as show_banner %}
    {% if show_banner %}
        <div class="banner">Big sale active!</div>
    {% endif %}
</footer>
```