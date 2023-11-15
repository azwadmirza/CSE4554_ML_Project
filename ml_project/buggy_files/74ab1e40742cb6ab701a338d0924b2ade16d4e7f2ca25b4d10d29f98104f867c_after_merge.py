    def _extract_filters(self, queryparams=None):
        """Extracts filters from QueryString parameters."""
        if not queryparams:
            queryparams = self.request.GET

        filters = []

        for param, paramvalue in queryparams.items():
            param = param.strip()

            error_details = {
                'name': param,
                'location': 'querystring',
                'description': 'Invalid value for %s' % param
            }

            # Ignore specific fields
            if param.startswith('_') and param not in ('_since',
                                                       '_to',
                                                       '_before'):
                continue

            # Handle the _since specific filter.
            if param in ('_since', '_to', '_before'):
                value = native_value(paramvalue.strip('"'))

                if not isinstance(value, six.integer_types):
                    raise_invalid(self.request, **error_details)

                if param == '_since':
                    operator = COMPARISON.GT
                else:
                    if param == '_to':
                        message = ('_to is now deprecated, '
                                   'you should use _before instead')
                        url = ('http://cliquet.rtfd.org/en/2.4.0/api/resource'
                               '.html#list-of-available-url-parameters')
                        send_alert(self.request, message, url)
                    operator = COMPARISON.LT
                filters.append(
                    Filter(self.model.modified_field, value, operator)
                )
                continue

            m = re.match(r'^(min|max|not|lt|gt|in|exclude)_(\w+)$', param)
            if m:
                keyword, field = m.groups()
                operator = getattr(COMPARISON, keyword.upper())
            else:
                operator, field = COMPARISON.EQ, param

            if not self.is_known_field(field):
                error_msg = "Unknown filter field '{0}'".format(param)
                error_details['description'] = error_msg
                raise_invalid(self.request, **error_details)

            value = native_value(paramvalue)
            if operator in (COMPARISON.IN, COMPARISON.EXCLUDE):
                value = set([native_value(v) for v in paramvalue.split(',')])

                all_integers = all([isinstance(v, six.integer_types)
                                    for v in value])
                all_strings = all([isinstance(v, six.text_type)
                                   for v in value])
                has_invalid_value = (
                    (field == self.model.id_field and not all_strings) or
                    (field == self.model.modified_field and not all_integers)
                )
                if has_invalid_value:
                    raise_invalid(self.request, **error_details)

            filters.append(Filter(field, value, operator))

        return filters