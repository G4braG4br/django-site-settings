# Django Site Settings

[![PyPI version](https://img.shields.io/pypi/v/django-site-settings)](https://pypi.org/project/django-site-settings/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-site-settings)](https://pypi.org/project/django-site-settings/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT)

**Django Site Settings** is a reusable Django application designed to manage dynamic, type-safe global configurations directly from the Django Admin panel. Built on top of [django-solo](https://github.com/lazybird/django-solo), it guarantees a singleton pattern for your core settings while offering an advanced, customizable caching layer.

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

## Integration with `django-admin-reorder`

If you are using custom admin menu managers like `django-admin-reorder` to clean up your Django Admin sidebar, you need to explicitly list all three models provided by this package under your custom app layout. 

Add the following configuration block to your `settings.py`:

```python
ADMIN_REORDER = [
    # ... your other apps ...
    {
        "app": "django_site_settings",
        "label": "Site Settings Engine",
        "models": (
            "django_site_settings.Settings",
            "django_site_settings.SiteAnnouncement",
            "django_site_settings.SettingAccessGroup",
        ),
    },
]
```

## Usage
### Admin Panel Interface
Once installed and configured, a new section called Site Settings Engine will automatically appear in your main Django administration index:

<p align="center">
<img width="800" style="max-width: 100%;" alt="image_usage_1" src="https://github.com/user-attachments/assets/9409819c-9d88-4432-927c-c8f1011df9c9" />
</p>


Global Configuration Management
Clicking on Global Configuration provides a clean, unified dashboard where you can manage all custom variables as transactional setting items.

Empty State: Upon initialization, the dashboard presents a clean tabular inline structure layout, ready for keys assignment:

<p align="center">
<img width="800" style="max-width: 100%;" alt="image_usage_2" src="https://github.com/user-attachments/assets/a670b509-a1fb-4417-aac3-f5050407fe94" />
</p>


Populated State with Validation: You can dynamically add keys, provide descriptive notes for your team, select strict target data types (e.g., Boolean, Float), and input their corresponding values natively:

<p align="center">
<img width="800" style="max-width: 100%;" alt="image_usage_3" src="https://github.com/user-attachments/assets/f2ee2f87-de12-4283-a240-0a915bc51c34" />
</p>


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

## Advanced Features: Global Site Announcements

The `django-site-settings` package includes a built-in notification engine powered by the `SiteAnnouncement` model. This feature allows administrators to broadcast multiple urgent alerts, maintenance windows, or marketing banners across the platform simultaneously, mimicking enterprise-tier SaaS announcement architectures.

### Key Highlights
* **Stacked Alerts Support**: Display multiple active notifications at once.
* **Smart Priority Sorting**: Announcements are automatically arranged based on a customizable `priority` scale (e.g., critical `danger` alerts float to the top).
* **Automated Lifecycles**: Schedule banners to activate (`start_at`) and expire (`end_at`) autonomously.
* **Data-Level Caching**: Active records are evaluated into a memory-efficient Python list layer and cached (`cache.get`/`cache.set`), reducing database serialization overhead down to zero under high concurrent traffic.
* **Instant Cache Invalidation**: Overridden `save()` and `delete()` model hooks flush the cache immediately when an administrator updates or removes a record.
* **Hybrid Frontend Integration**: Choose between native Django Template Tags or a lightweight REST API endpoint.
* **Independent Client-side Dismissal**: Users can close individual banners. Closure states are safely tracked in browser `localStorage` using individual record IDs and atomic version timestamps (`updated_at`) to avoid redundant database or session overhead.

---

### Implementation Guide

#### Integration via REST API (SPA / Headless Architecture)
### Step A: Include Routing
Register the library's URL patterns inside your root Django urls.py configuration:

```python
from django.urls import path, include

urlpatterns = [
    # ... your core project routes
    path("site-settings/", include("django_site_settings.urls")),
]
```

### Step B: Consume the Endpoint
Your frontend application can fetch or poll from the following cache-backed public URI:
GET /site-settings/api/announcements/

Example JSON Response Payload:

```json
{
  "announcements": [
    {
      "id": 4,
      "text": "<strong>Urgent:</strong> Scheduled system upgrade on June 8th at 03:00 UTC.",
      "level": "danger",
      "updated_at": 1780920000.0
    },
    {
      "id": 2,
      "text": "Check out our new metrics dashboard module!",
      "level": "info",
      "updated_at": 1780845200.0
    }
  ]
}
```

## Role-Based Access Control (RBAC)

For projects with hundreds of settings, you can dynamically restrict which configurations are visible and editable by specific groups of staff members (e.g., Marketing, DevOps, Support).

The package uses an explicit **Entity-Attribute-Value (EAV)** approach combined with Django's native `auth.Group` model via structured through-tables. Non-superuser staff will only see the configuration items explicitly assigned to their roles.

### Configuration via Django Admin

1. **Create Access Groups**: Go to **Setting Access Groups** in the Django Admin.
2. **Assign Staff Roles**: Select the standard Django user groups that should inherit these permissions.
3. **Map Settings**: Choose the explicit `AppSetting` records that these groups are authorized to manage.

When a restricted user opens the **Global Configuration** singleton panel, the under-the-hood `get_formset` interceptor dynamically filters database queries. Unauthorized settings are completely hidden from the user's view, preventing accidental overrides of critical production values.


### Security & HTML Sanitization

To allow rich-text formatting (such as links, bold text, lists, and headings) in backend-driven banners while maintaining strict security boundaries, the `SiteAnnouncement.text` field uses a custom `SanitizedHTMLField`.

This field eliminates the risk of **Stored Cross-Site Scripting (XSS)** attacks. Whenever an announcement is saved, the library automatically intercepts the input and strips out malicious scripts, dangerous handlers (e.g., `onerror`, `onclick`), and unauthorized tags before they can ever reach your PostgreSQL database.

### Under the Hood

The sanitization engine is powered by **`nh3`** (a lightning-fast, secure HTML sanitizer built on top of Rust's `ammonia` library - https://pypi.org/project/nh3/). 

```python
DEFAULT_ALLOWED_TAGS = {"a", "b", "i", "strong", "em", "p", "br", "span", "ul", "ol", "li", "h1", "h2", "h3"}
DEFAULT_ALLOWED_ATTRIBUTES = {
    "a": {"href", "title", "target"},
    "span": {"class", "style"},
}
```
