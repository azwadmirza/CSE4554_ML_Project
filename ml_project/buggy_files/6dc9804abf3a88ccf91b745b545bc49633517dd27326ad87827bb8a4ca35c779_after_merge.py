    def from_string_spec(cls, string_spec):
        impl, major, minor, micro, arch, path = None, None, None, None, None, None
        if os.path.isabs(string_spec):
            path = string_spec
        else:
            ok = False
            match = re.match(PATTERN, string_spec)
            if match:

                def _int_or_none(val):
                    return None if val is None else int(val)

                try:
                    groups = match.groupdict()
                    version = groups["version"]
                    if version is not None:
                        versions = tuple(int(i) for i in version.split(".") if i)
                        if len(versions) > 3:
                            raise ValueError
                        if len(versions) == 3:
                            major, minor, micro = versions
                        elif len(versions) == 2:
                            major, minor = versions
                        elif len(versions) == 1:
                            version_data = versions[0]
                            major = int(str(version_data)[0])  # first digit major
                            if version_data > 9:
                                minor = int(str(version_data)[1:])
                    ok = True
                except ValueError:
                    pass
                else:
                    impl = groups["impl"]
                    if impl == "py" or impl == "python":
                        impl = "CPython"
                    arch = _int_or_none(groups["arch"])

            if not ok:
                path = string_spec

        return cls(string_spec, impl, major, minor, micro, arch, path)