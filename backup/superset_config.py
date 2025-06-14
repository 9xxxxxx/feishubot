FEATURE_FLAGS = {
"DASHBOARD_NATIVE_FILTERS": True,
"DASHBOARD_NATIVE_FILTERS_SET": True,
"DASHBOARD_CROSS_FILTERS": True, 
"HORIZONTAL_FILTER_BAR": True ,
"ENABLE_TEMPLATE_PROCESSING": True,
"ESCAPE_MARKDOWN_HTML": False,
"ALERT_REPORTS": True,
"ENABLE_JAVASCRIPT_CONTROLS":True,
"ALLOW_TEMPLATE_JAVASCRIPT": True,
"ALLOW_ADHOC_SUBQUERY":True,
"EMBEDDED_SUPERSET": True,
"DYNAMIC_PLUGINS": True,
"DRILL_TO_DETAIL": True,
"VERSIONED_EXPORT": True,
"DASHBOARD_RBAC": True,
"GENERIC_CHART_AXES": True
}


TALISMAN_CONFIG = {
    "content_security_policy": {
        "default-src": ["'self'"],
        "img-src": ["'self'", "blob:", "data:"],
        "worker-src": ["'self'", "blob:"],
        "connect-src": [
            "'self'",
            "https://api.mapbox.com",
            "https://events.mapbox.com",
        ],
        "object-src": "'none'",
        "style-src": [
            "'self'",
            "'unsafe-inline'",
        ],
        "script-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
    },
    "content_security_policy_nonce_in": ["script-src"],
    "force_https": False,
}

TALISMAN_ENABLED = False
HTML_SANITIZATION = True
WTF_CSRF_ENABLED = False


HTML_SANITIZATION_SCHEMA_EXTENSIONS = {
  "attributes": {
    "*": ["className"],
  },
  "tagNames": ["style"],
}

FAB_API_SWAGGER_UI = True

CSV_EXPORT = {"encoding": "utf-8-sig"}

SECRET_KEY = 'ybVTykhS/4QfwOYkPb5c50AE6udnEfKLq0nueJayyIGE2SMLzUjA7mix'


BABEL_DEFAULT_LOCALE = "zh"

LANGUAGES = {
   "zh": {"flag": "cn", "name": "简体中文"},
   "en": {"flag": "us", "name": "English"},
}

# default row limit when requesting samples from datasource in explore view
SAMPLES_ROW_LIMIT = 10000
# default row limit for native filters
NATIVE_FILTER_DEFAULT_ROW_LIMIT = 10000


DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 60 * 60, 
    'CACHE_KEY_PREFIX': 'superset_results',
    'CACHE_REDIS_URL': 'redis://:redis_6379@localhost:6379/0',  # Redis 地址
}

