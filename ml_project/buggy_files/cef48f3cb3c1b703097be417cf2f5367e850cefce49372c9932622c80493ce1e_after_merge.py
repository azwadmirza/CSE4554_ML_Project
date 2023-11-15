    def stringize(key, value, ignored_keys, indent, in_list=False):
        if not isinstance(key, (str, unicode)):
            raise NetworkXError('%r is not a string' % (key,))
        if not valid_keys.match(key):
            raise NetworkXError('%r is not a valid key' % (key,))
        if not isinstance(key, str):
            key = str(key)
        if key not in ignored_keys:
            if isinstance(value, (int, long, bool)):
                if key == 'label':
                    yield indent + key + ' "' + str(value) + '"'
                elif value is True:
                    # python bool is an instance of int
                    yield indent + key + ' 1'
                elif value is False:
                    yield indent + key + ' 0'
                else:
                    yield indent + key + ' ' + str(value)
            elif isinstance(value, float):
                text = repr(value).upper()
                # GML requires that a real literal contain a decimal point, but
                # repr may not output a decimal point when the mantissa is
                # integral and hence needs fixing.
                epos = text.rfind('E')
                if epos != -1 and text.find('.', 0, epos) == -1:
                    text = text[:epos] + '.' + text[epos:]
                if key == 'label':
                    yield indent + key + ' "' + test + '"'
                else:
                    yield indent + key + ' ' + text
            elif isinstance(value, dict):
                yield indent + key + ' ['
                next_indent = indent + '  '
                for key, value in value.items():
                    for line in stringize(key, value, (), next_indent):
                        yield line
                yield indent + ']'
            elif isinstance(value, (list, tuple)) and key != 'label' \
                            and value and not in_list:
                next_indent = indent + '  '
                for val in value:
                    for line in stringize(key, val, (), next_indent, True):
                        yield line
            else:
                if stringizer:
                    try:
                        value = stringizer(value)
                    except ValueError:
                        raise NetworkXError(
                            '%r cannot be converted into a string' % (value,))
                if not isinstance(value, (str, unicode)):
                    raise NetworkXError('%r is not a string' % (value,))
                yield indent + key + ' "' + escape(value) + '"'