def time_convert(length) -> int:
    match = _RE_TIME_CONVERTER.match(length)
    if match is not None:
        hr = int(match.group(1)) if match.group(1) else 0
        mn = int(match.group(2)) if match.group(2) else 0
        sec = int(match.group(3)) if match.group(3) else 0
        pos = sec + (mn * 60) + (hr * 3600)
        return pos
    else:
        try:
            return int(length)
        except ValueError:
            return 0