    def __init__(self, address):
        '''
        Instantiate a new IPv6 address object. Scope is moved to an attribute 'scope'.

        Args:
            address: A string or integer representing the IP

              Additionally, an integer can be passed, so
              IPv6Address('2001:db8::') == IPv6Address(42540766411282592856903984951653826560)
              or, more generally
              IPv6Address(int(IPv6Address('2001:db8::'))) == IPv6Address('2001:db8::')

        Raises:
            AddressValueError: If address isn't a valid IPv6 address.

        :param address:
        '''
        if isinstance(address, string_types) and '%' in address:
            buff = address.split('%')
            if len(buff) != 2:
                raise SaltException('Invalid IPv6 address: "{}"'.format(address))
            address, self.__scope = buff
        else:
            self.__scope = None

        if sys.version_info.major == 2:
            ipaddress._BaseAddress.__init__(self, address)
            ipaddress._BaseV6.__init__(self, address)
        else:
            # Python 3.4 fix. Versions higher are simply not affected
            # https://github.com/python/cpython/blob/3.4/Lib/ipaddress.py#L543-L544
            self._version = 6
            self._max_prefixlen = ipaddress.IPV6LENGTH

        # Efficient constructor from integer.
        if isinstance(address, integer_types):
            self._check_int_address(address)
            self._ip = address
        elif self._is_packed_binary(address):
            self._check_packed_address(address, 16)
            self._ip = ipaddress._int_from_bytes(address, 'big')
        else:
            address = str(address)
            if '/' in address:
                raise ipaddress.AddressValueError("Unexpected '/' in {}".format(address))
            self._ip = self._ip_int_from_string(address)