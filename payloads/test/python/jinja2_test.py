test_payloads = [
    {
        "payload": "{{7*7}}",
        "expected": "49",
        "engine": "Jinja2"
    },
    {
        "payload": "{{''.__class__.__mro__[1].__subclasses__()[40]}}",
        "expected": "<class 'warnings.WarningMessage'>" or "<class 'list_iterator'>", 
        "engine": "Jinja2"
    },
    {
        "payload": "{{-42}}",
        "expected": "-42",
        "engine": "Jinja2"
    },
    {
        "payload": "{{42//5}}",
        "expected": "8",
        "engine": "Jinja2"
    },
    {
        "payload": "{{1337|abs}}",
        "expected": "1337",
        "engine": "Jinja2"
    },
    {
        "payload": "{{'S'+'STI'}}",
        "expected": "SSTI",
        "engine": "Jinja2"
    },
    {
        "payload": "{{(10**2)}}",
        "expected": "100",
        "engine": "Jinja2"
    },
    {
        "payload": "{{ (3.14|round) }}",
        "expected": "3",
        "engine": "Jinja2"
    },
    {
        "payload": "{{ [1,2,3][1] }}",
        "expected": "2",
        "engine": "Jinja2"
    },
    {
        "payload": "{{ {'a':123}['a'] }}",
        "expected": "123",
        "engine": "Jinja2"
    }
]
