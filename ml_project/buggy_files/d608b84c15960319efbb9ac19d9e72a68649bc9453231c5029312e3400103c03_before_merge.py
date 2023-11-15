    def for_interpreter(cls, interpreter):
        key_to_class, key_to_meta, builtin_key, describe = OrderedDict(), {}, None, None
        for key, creator_class in cls.options("virtualenv.create").items():
            if key == "builtin":
                raise RuntimeError("builtin creator is a reserved name")
            meta = creator_class.can_create(interpreter)
            if meta:
                if "builtin" not in key_to_class and issubclass(creator_class, VirtualenvBuiltin):
                    builtin_key = key
                    key_to_class["builtin"] = creator_class
                    key_to_meta["builtin"] = meta
                key_to_class[key] = creator_class
                key_to_meta[key] = meta
            if describe is None and issubclass(creator_class, Describe) and creator_class.can_describe(interpreter):
                describe = creator_class
        return CreatorInfo(
            key_to_class=key_to_class, key_to_meta=key_to_meta, describe=describe, builtin_key=builtin_key
        )