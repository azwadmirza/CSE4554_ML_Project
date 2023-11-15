    def dumps(self, msg, use_bin_type=False):
        '''
        Run the correct dumps serialization format

        :param use_bin_type: Useful for Python 3 support. Tells msgpack to
                             differentiate between 'str' and 'bytes' types
                             by encoding them differently.
                             Since this changes the wire protocol, this
                             option should not be used outside of IPC.
        '''
        def ext_type_encoder(obj):
            if isinstance(obj, six.integer_types):
                # msgpack can't handle the very long Python longs for jids
                # Convert any very long longs to strings
                return six.text_type(obj)
            elif isinstance(obj, (datetime.datetime, datetime.date)):
                # msgpack doesn't support datetime.datetime and datetime.date datatypes.
                # So here we have converted these types to custom datatype
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
            elif isinstance(obj, CaseInsensitiveDict):
                return dict(obj)
            # Nothing known exceptions found. Let msgpack raise it's own.
            return obj

        try:
            if msgpack.version >= (0, 4, 0):
                # msgpack only supports 'use_bin_type' starting in 0.4.0.
                # Due to this, if we don't need it, don't pass it at all so
                # that under Python 2 we can still work with older versions
                # of msgpack.
                return salt.utils.msgpack.dumps(msg, default=ext_type_encoder,
                                                use_bin_type=use_bin_type,
                                                _msgpack_module=msgpack)
            else:
                return salt.utils.msgpack.dumps(msg, default=ext_type_encoder,
                                                _msgpack_module=msgpack)
        except (OverflowError, msgpack.exceptions.PackValueError):
            # msgpack<=0.4.6 don't call ext encoder on very long integers raising the error instead.
            # Convert any very long longs to strings and call dumps again.
            def verylong_encoder(obj, context):
                # Make sure we catch recursion here.
                objid = id(obj)
                if objid in context:
                    return '<Recursion on {} with id={}>'.format(type(obj).__name__, id(obj))
                context.add(objid)

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

            msg = verylong_encoder(msg, set())
            if msgpack.version >= (0, 4, 0):
                return salt.utils.msgpack.dumps(msg, default=ext_type_encoder,
                                                use_bin_type=use_bin_type,
                                                _msgpack_module=msgpack)
            else:
                return salt.utils.msgpack.dumps(msg, default=ext_type_encoder,
                                                _msgpack_module=msgpack)