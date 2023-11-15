    def validate_host_filter(self, host_filter):
        if host_filter:
            try:
                for match in JSONBField.get_lookups().keys():
                    if match == 'exact':
                        # __exact is allowed
                        continue
                    match = '__{}'.format(match)
                    if re.match(
                        'ansible_facts[^=]+{}='.format(match),
                        host_filter
                    ):
                        raise models.base.ValidationError({
                            'host_filter': 'ansible_facts does not support searching with {}'.format(match)
                        })
                SmartFilter().query_from_string(host_filter)
            except RuntimeError as e:
                raise models.base.ValidationError(e)
        return host_filter