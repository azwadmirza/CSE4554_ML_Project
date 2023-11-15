    def handle_check(self, command, **options):
        """Check your settings for common misconfigurations"""
        passed = True
        client = DjangoClient()
        # check if org/app and token are set:
        is_set = lambda x: x and x != 'None'
        values = [client.config.service_name, client.config.secret_token]
        if all(map(is_set, values)):
            self.write(
                'Service name and secret token are set, good job!',
                green
            )
        else:
            passed = False
            self.write(
                'Configuration errors detected!', red, ending='\n\n'
            )
            if not is_set(client.config.service_name):
                self.write("  * SERVICE_NAME not set! ", red, ending='\n')
            if not is_set(client.config.secret_token):
                self.write("  * SECRET_TOKEN not set!", red, ending='\n')
            self.write(CONFIG_EXAMPLE)
        self.write('')

        # check if we're disabled due to DEBUG:
        if settings.DEBUG:
            if getattr(settings, 'ELASTIC_APM', {}).get('DEBUG'):
                self.write(
                    'Note: even though you are running in DEBUG mode, we will '
                    'send data to the APM Server, because you set ELASTIC_APM["DEBUG"] to '
                    'True. You can disable ElasticAPM while in DEBUG mode like this'
                    '\n\n',
                    yellow
                )
                self.write(
                    '   ELASTIC_APM = {\n'
                    '       "DEBUG": False,\n'
                    '       # your other ELASTIC_APM settings\n'
                    '   }'

                )
            else:
                self.write(
                    'Looks like you\'re running in DEBUG mode. ElasticAPM will NOT '
                    'gather any data while DEBUG is set to True.\n\n',
                    red,
                )
                self.write(
                    'If you want to test ElasticAPM while DEBUG is set to True, you'
                    ' can force ElasticAPM to gather data by setting'
                    ' ELASTIC_APM["DEBUG"] to True, like this\n\n'
                    '   ELASTIC_APM = {\n'
                    '       "DEBUG": True,\n'
                    '       # your other ELASTIC_APM settings\n'
                    '   }'
                )
                passed = False
        else:
            self.write(
                'DEBUG mode is disabled! Looking good!',
                green
            )
        self.write('')

        # check if middleware is set, and if it is at the first position
        middleware_attr = 'MIDDLEWARE' if getattr(settings, 'MIDDLEWARE', None) is not None else 'MIDDLEWARE_CLASSES'
        middleware = list(getattr(settings, middleware_attr))
        try:
            pos = middleware.index('elasticapm.contrib.django.middleware.TracingMiddleware')
            if pos == 0:
                self.write('Tracing middleware is configured! Awesome!', green)
            else:
                self.write('Tracing middleware is configured, but not at the first position\n', yellow)
                self.write('ElasticAPM works best if you add it at the top of your %s setting' % middleware_attr)
        except ValueError:
            self.write('Tracing middleware not configured!', red)
            self.write(
                '\n'
                'Add it to your %(name)s setting like this:\n\n'
                '    %(name)s = (\n'
                '        "elasticapm.contrib.django.middleware.TracingMiddleware",\n'
                '        # your other middleware classes\n'
                '    )\n' % {'name': middleware_attr}
            )
        self.write('')
        if passed:
            self.write('Looks like everything should be ready!', green)
        else:
            self.write(
                'Please fix the above errors.',
                red
            )
        self.write('')
        return passed