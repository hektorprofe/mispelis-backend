# S11 Docker

## C01 Presentación

## C02 Backend (python + django + redis + postgres)

# Si estamos en un entorno de producción usando un dominio

```python
# settings.py django

if not DEBUG:

    MEDIA_URL = 'https://www.ejemplo.com/media/'

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_DOMAIN = ".ejemplo.com"
    CORS_ORIGIN_WHITELIST = [
        "https://www.ejemplo.com"
    ]
```
