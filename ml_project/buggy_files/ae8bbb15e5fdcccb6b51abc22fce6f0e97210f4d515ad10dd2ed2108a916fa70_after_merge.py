def to_lines(stdout):
    for item in stdout:
        if isinstance(item, string_types):
            item = to_text(item).split('\n')
        yield item