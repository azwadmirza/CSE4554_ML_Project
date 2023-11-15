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
                # A value of an Integer object is limited from -(2^63) upto (2^64)-1 by MessagePack
                # spec. Here we care only of JIDs that are positive integers.
                if isinstance(obj, six.integer_types) and obj >= pow(2, 64):
                    return six.text_type(obj)
                else:
                    return obj