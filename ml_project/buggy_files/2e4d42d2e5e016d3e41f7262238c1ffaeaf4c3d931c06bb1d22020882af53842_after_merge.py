def _make_hash(cls, attrs, frozen, cache_hash):
    attrs = tuple(
        a for a in attrs if a.hash is True or (a.hash is None and a.eq is True)
    )

    tab = "        "

    unique_filename = _generate_unique_filename(cls, "hash")
    type_hash = hash(unique_filename)

    hash_def = "def __hash__(self"
    hash_func = "hash(("
    closing_braces = "))"
    if not cache_hash:
        hash_def += "):"
    else:
        if not PY2:
            hash_def += ", *"

        hash_def += (
            ", _cache_wrapper="
            + "__import__('attr._make')._make._CacheHashWrapper):"
        )
        hash_func = "_cache_wrapper(" + hash_func
        closing_braces += ")"

    method_lines = [hash_def]

    def append_hash_computation_lines(prefix, indent):
        """
        Generate the code for actually computing the hash code.
        Below this will either be returned directly or used to compute
        a value which is then cached, depending on the value of cache_hash
        """

        method_lines.extend(
            [
                indent + prefix + hash_func,
                indent + "        %d," % (type_hash,),
            ]
        )

        for a in attrs:
            method_lines.append(indent + "        self.%s," % a.name)

        method_lines.append(indent + "    " + closing_braces)

    if cache_hash:
        method_lines.append(tab + "if self.%s is None:" % _hash_cache_field)
        if frozen:
            append_hash_computation_lines(
                "object.__setattr__(self, '%s', " % _hash_cache_field, tab * 2
            )
            method_lines.append(tab * 2 + ")")  # close __setattr__
        else:
            append_hash_computation_lines(
                "self.%s = " % _hash_cache_field, tab * 2
            )
        method_lines.append(tab + "return self.%s" % _hash_cache_field)
    else:
        append_hash_computation_lines("return ", tab)

    script = "\n".join(method_lines)
    return _make_method("__hash__", script, unique_filename)