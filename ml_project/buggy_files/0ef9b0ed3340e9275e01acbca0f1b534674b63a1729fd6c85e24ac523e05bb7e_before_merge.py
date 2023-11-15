def parse_urilist(data):
    result = []
    for line in data.splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        try:
            validation.check_uri(line)
        except ValueError:
            return []
        result.append(line)
    return result