            def verylong_encoder(obj):
                if isinstance(obj, dict):
                    for key, value in six.iteritems(obj.copy()):
                        obj[key] = verylong_encoder(value)
                    return dict(obj)
                elif isinstance(obj, (list, tuple)):
                    obj = list(obj)
                    for idx, entry in enumerate(obj):
                        obj[idx] = verylong_encoder(entry)
                    return obj
                # This is a spurious lint failure as we are gating this check
                # behind a check for six.PY2.
                if six.PY2 and isinstance(obj, long) and long > pow(2, 64):  # pylint: disable=incompatible-py3-code
                    return six.text_type(obj)
                elif six.PY3 and isinstance(obj, int) and int > pow(2, 64):
                    return six.text_type(obj)
                else:
                    return obj