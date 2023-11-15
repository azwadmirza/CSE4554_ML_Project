    def add_to_params(self, parameters, value):
        if value:
            try:
                if value == '-1' or value == 'all':
                    fromstr = '-1'
                    tostr = '-1'
                elif '-' in value:
                    # We can get away with simple logic here because
                    # argparse will not allow values such as
                    # "-1-8", and these aren't actually valid
                    # values any from from/to ports.
                    fromstr, tostr = value.split('-', 1)
                else:
                    fromstr, tostr = (value, value)
                _build_ip_permissions(parameters, 'FromPort', int(fromstr))
                _build_ip_permissions(parameters, 'ToPort', int(tostr))
            except ValueError:
                msg = ('port parameter should be of the '
                       'form <from[-to]> (e.g. 22 or 22-25)')
                raise ValueError(msg)