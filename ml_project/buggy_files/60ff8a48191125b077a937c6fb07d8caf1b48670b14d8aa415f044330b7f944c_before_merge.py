def build_message(specs):
    return "\n".join([s.msg for s in specs if s.msg is not None])