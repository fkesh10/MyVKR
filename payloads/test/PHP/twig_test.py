test_payloads = [
    {
        "payload": "{{ 7 * 7 }}",
        "expected": "49",
        "engine": "Twig"
    },
    {
        "payload": "{{ 'S' ~ 'STI' }}",
        "expected": "SSTI",
        "engine": "Twig"
    },
    {
        "payload": "{{ [1, 2, 3]|length }}",
        "expected": "3",
        "engine": "Twig"
    },
    {
        "payload": "{{ 'abc123'|replace({'123':'XYZ'}) }}",
        "expected": "abcXYZ",
        "engine": "Twig"
    },
    {
        "payload": "{{ 'abc'|upper }}",
        "expected": "ABC",
        "engine": "Twig"
    },
    {
        "payload": "{{ 'TeSt'|lower }}",
        "expected": "test",
        "engine": "Twig"
    },
    {
        "payload": "{{ [1, 2, 3]|join(',') }}",
        "expected": "1,2,3",
        "engine": "Twig"
    },
    {
        "payload": "{{ '1234567890'|slice(0,4) }}",
        "expected": "1234",
        "engine": "Twig"
    },
    {
        "payload": "{{ ['a','b','c']|first }}",
        "expected": "a",
        "engine": "Twig"
    },
    {
        "payload": "{{ 'twig' starts with 't' }}",
        "expected": "1",  # true как 1
        "engine": "Twig"
    }
]
