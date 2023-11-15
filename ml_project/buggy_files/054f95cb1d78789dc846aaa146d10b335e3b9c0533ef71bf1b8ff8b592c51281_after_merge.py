    def is_valid(value: str, sanitize: bool = False) -> bool:
        if sanitize:
            value = IPAddress().sanitize(value)

        if not GenericType().is_valid(value):
            return False

        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            return False

        if address == ipaddress.ip_address('0.0.0.0'):
            return False

        if '%' in address:
            # IPv6 address with scope ID
            # https://github.com/certtools/intelmq/issues/1550
            return False

        return True