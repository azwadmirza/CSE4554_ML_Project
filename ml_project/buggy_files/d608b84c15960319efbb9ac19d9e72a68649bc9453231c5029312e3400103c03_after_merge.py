    def for_interpreter(cls, interpreter):
        key_to_class, key_to_meta, builtin_key, describe = OrderedDict(), {}, None, None
        errored = defaultdict(list)
        for key, creator_class in cls.options("virtualenv.create").items():
            if key == "builtin":
                raise RuntimeError("builtin creator is a reserved name")
            meta = creator_class.can_create(interpreter)
            if meta:
                if meta.error:
                    errored[meta.error].append(creator_class)
                else:
                    if "builtin" not in key_to_class and issubclass(creator_class, VirtualenvBuiltin):
                        builtin_key = key
                        key_to_class["builtin"] = creator_class
                        key_to_meta["builtin"] = meta
                    key_to_class[key] = creator_class
                    key_to_meta[key] = meta
            if describe is None and issubclass(creator_class, Describe) and creator_class.can_describe(interpreter):
                describe = creator_class
        if not key_to_meta:
            if errored:
                raise RuntimeError(
                    "\n".join(
                        "{} for creators {}".format(k, ", ".join(i.__name__ for i in v)) for k, v in errored.items()
                    )
                )
            else:
                raise RuntimeError("No virtualenv implementation for {}".format(interpreter))
        return CreatorInfo(
            key_to_class=key_to_class, key_to_meta=key_to_meta, describe=describe, builtin_key=builtin_key
        )