    def process_value_type(self, sentinel, value, resource):
        if self.vtype == 'normalize' and isinstance(value, str):
            return sentinel, value.strip().lower()

        elif self.vtype == 'expr':
            sentinel = self.get_resource_value(sentinel, resource)
            return sentinel, value

        elif self.vtype == 'integer':
            try:
                value = int(str(value).strip())
            except ValueError:
                value = 0
        elif self.vtype == 'size':
            try:
                return sentinel, len(value)
            except TypeError:
                return sentinel, 0
        elif self.vtype == 'unique_size':
            try:
                return sentinel, len(set(value))
            except TypeError:
                return sentinel, 0
        elif self.vtype == 'swap':
            return value, sentinel
        elif self.vtype == 'date':
            return parse_date(sentinel), parse_date(value)
        elif self.vtype == 'age':
            if not isinstance(sentinel, datetime.datetime):
                sentinel = datetime.datetime.now(tz=tzutc()) - timedelta(sentinel)
            value = parse_date(value)
            if value is None:
                # compatiblity
                value = 0
            # Reverse the age comparison, we want to compare the value being
            # greater than the sentinel typically. Else the syntax for age
            # comparisons is intuitively wrong.
            return value, sentinel
        elif self.vtype == 'cidr':
            s = parse_cidr(sentinel)
            v = parse_cidr(value)
            if (isinstance(s, ipaddress._BaseAddress) and isinstance(v, ipaddress._BaseNetwork)):
                return v, s
            return s, v
        elif self.vtype == 'cidr_size':
            cidr = parse_cidr(value)
            if cidr:
                return sentinel, cidr.prefixlen
            return sentinel, 0

        # Allows for expiration filtering, for events in the future as opposed
        # to events in the past which age filtering allows for.
        elif self.vtype == 'expiration':
            if not isinstance(sentinel, datetime.datetime):
                sentinel = datetime.datetime.now(tz=tzutc()) + timedelta(sentinel)
            value = parse_date(value)
            if value is None:
                value = 0
            return sentinel, value

        # Allows for comparing version numbers, for things that you expect a minimum version number.
        elif self.vtype == 'version':
            s = ComparableVersion(sentinel)
            v = ComparableVersion(value)
            return s, v

        return sentinel, value