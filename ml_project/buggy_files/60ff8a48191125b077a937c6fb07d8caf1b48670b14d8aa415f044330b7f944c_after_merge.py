def build_message(specs):
    binstar_spec = next((spec for spec in specs if isinstance(spec, BinstarSpec)), None)
    if binstar_spec:
        return binstar_spec.msg
    else:
        return "\n".join([s.msg for s in specs if s.msg is not None])