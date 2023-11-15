    def _resolve_to_system(cls, target):
        start_executable = target.executable
        prefixes = OrderedDict()
        while target.system_executable is None:
            prefix = target.real_prefix or target.base_prefix or target.prefix
            if prefix in prefixes:
                if len(prefixes) == 1:
                    # if we're linking back to ourselves accept ourselves with a WARNING
                    logging.info("%r links back to itself via prefixes", target)
                    target.system_executable = target.executable
                    break
                for at, (p, t) in enumerate(prefixes.items(), start=1):
                    logging.error("%d: prefix=%s, info=%r", at, p, t)
                logging.error("%d: prefix=%s, info=%r", len(prefixes) + 1, prefix, target)
                raise RuntimeError("prefixes are causing a circle {}".format("|".join(prefixes.keys())))
            prefixes[prefix] = target
            target = target.discover_exe(prefix=prefix, exact=False)
        if target.executable != target.system_executable:
            target = cls.from_exe(target.system_executable)
        target.executable = start_executable
        return target