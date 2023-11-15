def parse_dest_level(line, dest, name):
    dest_level = None

    def parse_match(match):
        level = None
        if match:
            if int(match.group(1)) in range(0, 8):
                level = match.group(1)
            else:
                pass
        return level

    if dest is not None:
        if dest == 'logfile':
            match = re.search(r'logging logfile {} (\S+)'.format(name), line, re.M)
            if match:
                dest_level = parse_match(match)

        elif dest == 'server':
            match = re.search(r'logging server (?:\S+) (\d+)', line, re.M)
            if match:
                dest_level = parse_match(match)
        else:
            match = re.search(r'logging {} (\S+)'.format(dest), line, re.M)
            if match:
                dest_level = parse_match(match)

    return dest_level