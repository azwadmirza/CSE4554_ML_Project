        def ext_type_encoder(obj):
            if isinstance(obj, six.integer_types):
                # msgpack can't handle the very long Python longs for jids
                # Convert any very long longs to strings
                return six.text_type(obj)
            elif isinstance(obj, datetime.datetime):
                # msgpack doesn't support datetime.datetime datatype
                # So here we have converted datetime.datetime to custom datatype
                # This is msgpack Extended types numbered 78
                return msgpack.ExtType(78, salt.utils.stringutils.to_bytes(
                    obj.strftime('%Y%m%dT%H:%M:%S.%f')))
            # The same for immutable types
            elif isinstance(obj, immutabletypes.ImmutableDict):
                return dict(obj)
            elif isinstance(obj, immutabletypes.ImmutableList):
                return list(obj)
            elif isinstance(obj, (set, immutabletypes.ImmutableSet)):
                # msgpack can't handle set so translate it to tuple
                return tuple(obj)
            # Nothing known exceptions found. Let msgpack raise it's own.
            return obj