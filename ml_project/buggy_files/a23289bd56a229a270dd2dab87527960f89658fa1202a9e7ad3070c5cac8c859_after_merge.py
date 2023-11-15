    def loads(self, msg, encoding=None, raw=False):
        '''
        Run the correct loads serialization format

        :param encoding: Useful for Python 3 support. If the msgpack data
                         was encoded using "use_bin_type=True", this will
                         differentiate between the 'bytes' type and the
                         'str' type by decoding contents with 'str' type
                         to what the encoding was set as. Recommended
                         encoding is 'utf-8' when using Python 3.
                         If the msgpack data was not encoded using
                         "use_bin_type=True", it will try to decode
                         all 'bytes' and 'str' data (the distinction has
                         been lost in this case) to what the encoding is
                         set as. In this case, it will fail if any of
                         the contents cannot be converted.
        '''
        try:
            def ext_type_decoder(code, data):
                if code == 78:
                    data = salt.utils.stringutils.to_unicode(data)
                    return datetime.datetime.strptime(data, '%Y%m%dT%H:%M:%S.%f')
                return data

            gc.disable()  # performance optimization for msgpack
            if msgpack.version >= (0, 4, 0):
                # msgpack only supports 'encoding' starting in 0.4.0.
                # Due to this, if we don't need it, don't pass it at all so
                # that under Python 2 we can still work with older versions
                # of msgpack.
                ret = msgpack.loads(msg, use_list=True, ext_hook=ext_type_decoder, encoding=encoding)
            else:
                ret = msgpack.loads(msg, use_list=True, ext_hook=ext_type_decoder)
            if six.PY3 and encoding is None and not raw:
                ret = salt.transport.frame.decode_embedded_strs(ret)
        except Exception as exc:
            log.critical(
                'Could not deserialize msgpack message. This often happens '
                'when trying to read a file not in binary mode. '
                'To see message payload, enable debug logging and retry. '
                'Exception: %s', exc
            )
            log.debug('Msgpack deserialization failure on message: %s', msg)
            gc.collect()
            raise
        finally:
            gc.enable()
        return ret