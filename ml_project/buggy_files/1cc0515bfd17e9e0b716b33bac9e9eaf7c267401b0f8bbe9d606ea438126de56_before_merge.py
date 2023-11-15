    def add_to_params(self, parameters, value):
        if value:
            try:
                if value == '-1' or value == 'all':
                    fromstr = '-1'
                    tostr = '-1'
                elif '-' in value:
                    fromstr, tostr = value.split('-')
                else:
                    fromstr, tostr = (value, value)
                _build_ip_permissions(parameters, 'FromPort', int(fromstr))
                _build_ip_permissions(parameters, 'ToPort', int(tostr))
            except ValueError:
                msg = ('port parameter should be of the '
                       'form <from[-to]> (e.g. 22 or 22-25)')
                raise ValueError(msg)