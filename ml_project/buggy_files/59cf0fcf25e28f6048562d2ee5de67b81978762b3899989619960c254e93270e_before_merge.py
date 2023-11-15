    def dumps(self, msg, use_bin_type=False):
        '''
        Run the correct dumps serialization format

        :param use_bin_type: Useful for Python 3 support. Tells msgpack to
                             differentiate between 'str' and 'bytes' types
                             by encoding them differently.
                             Since this changes the wire protocol, this
                             option should not be used outside of IPC.
        '''
        try:
            if msgpack.version >= (0, 4, 0):
                # msgpack only supports 'use_bin_type' starting in 0.4.0.
                # Due to this, if we don't need it, don't pass it at all so
                # that under Python 2 we can still work with older versions
                # of msgpack.
                return msgpack.dumps(msg, use_bin_type=use_bin_type)
            else:
                return msgpack.dumps(msg)
        except (OverflowError, msgpack.exceptions.PackValueError):
            # msgpack can't handle the very long Python longs for jids
            # Convert any very long longs to strings
            # We borrow the technique used by TypeError below
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
            if msgpack.version >= (0, 4, 0):
                return msgpack.dumps(verylong_encoder(msg), use_bin_type=use_bin_type)
            else:
                return msgpack.dumps(verylong_encoder(msg))
        except TypeError as e:
            # msgpack doesn't support datetime.datetime datatype
            # So here we have converted datetime.datetime to custom datatype
            # This is msgpack Extended types numbered 78
            def default(obj):
                return msgpack.ExtType(78, obj)

            def dt_encode(obj):
                datetime_str = obj.strftime("%Y%m%dT%H:%M:%S.%f")
                if msgpack.version >= (0, 4, 0):
                    return msgpack.packb(datetime_str, default=default, use_bin_type=use_bin_type)
                else:
                    return msgpack.packb(datetime_str, default=default)

            def datetime_encoder(obj):
                if isinstance(obj, dict):
                    for key, value in six.iteritems(obj.copy()):
                        encodedkey = datetime_encoder(key)
                        if key != encodedkey:
                            del obj[key]
                            key = encodedkey
                        obj[key] = datetime_encoder(value)
                    return dict(obj)
                elif isinstance(obj, (list, tuple)):
                    obj = list(obj)
                    for idx, entry in enumerate(obj):
                        obj[idx] = datetime_encoder(entry)
                    return obj
                if isinstance(obj, datetime.datetime):
                    return dt_encode(obj)
                else:
                    return obj

            def immutable_encoder(obj):
                log.debug('IMMUTABLE OBJ: %s', obj)
                if isinstance(obj, immutabletypes.ImmutableDict):
                    return dict(obj)
                if isinstance(obj, immutabletypes.ImmutableList):
                    return list(obj)
                if isinstance(obj, immutabletypes.ImmutableSet):
                    return set(obj)

            if "datetime.datetime" in six.text_type(e):
                if msgpack.version >= (0, 4, 0):
                    return msgpack.dumps(datetime_encoder(msg), use_bin_type=use_bin_type)
                else:
                    return msgpack.dumps(datetime_encoder(msg))
            elif "Immutable" in six.text_type(e):
                if msgpack.version >= (0, 4, 0):
                    return msgpack.dumps(msg, default=immutable_encoder, use_bin_type=use_bin_type)
                else:
                    return msgpack.dumps(msg, default=immutable_encoder)

            if msgpack.version >= (0, 2, 0):
                # Should support OrderedDict serialization, so, let's
                # raise the exception
                raise

            # msgpack is < 0.2.0, let's make its life easier
            # Since OrderedDict is identified as a dictionary, we can't
            # make use of msgpack custom types, we will need to convert by
            # hand.
            # This means iterating through all elements of a dictionary or
            # list/tuple
            def odict_encoder(obj):
                if isinstance(obj, dict):
                    for key, value in six.iteritems(obj.copy()):
                        obj[key] = odict_encoder(value)
                    return dict(obj)
                elif isinstance(obj, (list, tuple)):
                    obj = list(obj)
                    for idx, entry in enumerate(obj):
                        obj[idx] = odict_encoder(entry)
                    return obj
                return obj
            if msgpack.version >= (0, 4, 0):
                return msgpack.dumps(odict_encoder(msg), use_bin_type=use_bin_type)
            else:
                return msgpack.dumps(odict_encoder(msg))
        except (SystemError, TypeError) as exc:  # pylint: disable=W0705
            log.critical(
                'Unable to serialize message! Consider upgrading msgpack. '
                'Message which failed was %s, with exception %s', msg, exc
            )