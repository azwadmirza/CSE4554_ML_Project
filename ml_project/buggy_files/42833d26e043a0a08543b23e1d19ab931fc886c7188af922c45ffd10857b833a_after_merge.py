            def verylong_encoder(obj, context):
                # Make sure we catch recursion here.
                objid = id(obj)
                # This instance list needs to correspond to the types recursed
                # in the below if/elif chain. Also update
                # tests/unit/test_payload.py
                if objid in context and isinstance(obj, (dict, list, tuple)):
                    return '<Recursion on {} with id={}>'.format(type(obj).__name__, id(obj))
                context.add(objid)

                # The isinstance checks in this if/elif chain need to be
                # kept in sync with the above recursion check.
                if isinstance(obj, dict):
                    for key, value in six.iteritems(obj.copy()):
                        obj[key] = verylong_encoder(value, context)
                    return dict(obj)
                elif isinstance(obj, (list, tuple)):
                    obj = list(obj)
                    for idx, entry in enumerate(obj):
                        obj[idx] = verylong_encoder(entry, context)
                    return obj
                # A value of an Integer object is limited from -(2^63) upto (2^64)-1 by MessagePack
                # spec. Here we care only of JIDs that are positive integers.
                if isinstance(obj, six.integer_types) and obj >= pow(2, 64):
                    return six.text_type(obj)
                else:
                    return obj