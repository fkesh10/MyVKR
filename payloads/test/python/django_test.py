test_payloads = [
    {
        "payload": "{{10|add:5}}",
        "expected": "15",
        "engine": "Django"
    },
    {
        "payload": "{{'ab'|cut:'b'}}",
        "expected": "a",
        "engine": "Django"
    },
    {
        "payload": "{{'hello'|length}}",
        "expected": "5",
        "engine": "Django"
    },
    {
        "payload": "{{123456|slice:':3'}}",
        "expected": "123",
        "engine": "Django"
    },
    {
        "payload": "{{'HELLO'|lower}}",
        "expected": "hello",
        "engine": "Django"
    },
    {
        "payload": "{{'xyz'|yesno:'Y,N'}}",
        "expected": "Y",
        "engine": "Django"
    },
    {
        "payload": "{{''|yesno:'yes,no'}}",
        "expected": "no",
        "engine": "Django"
    },
    {
        "payload": "{{5|divisibleby:5}}",
        "expected": "True",
        "engine": "Django"
    },
    {
        "payload": "{{4|add:-2}}",
        "expected": "2",
        "engine": "Django"
    },
    {
        "payload": "{{None|default:'empty'}}",
        "expected": "empty",
        "engine": "Django"
    }
]
