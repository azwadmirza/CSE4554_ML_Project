def _parse_member(settype, member, strict=False):
    subtypes = settype.split(':')[1].split(',')

    parts = member.split(' ')

    parsed_member = []
    for i in range(len(subtypes)):
        subtype = subtypes[i]
        part = parts[i]

        if subtype in ['ip', 'net']:
            try:
                if '/' in part:
                    part = ipaddress.ip_network(part, strict=strict)
                elif '-' in part:
                    start, end = list(map(ipaddress.ip_address, part.split('-')))

                    part = list(ipaddress.summarize_address_range(start, end))
                else:
                    part = ipaddress.ip_address(part)
            except ValueError:
                pass

        elif subtype == 'port':
            part = int(part)

        parsed_member.append(part)

    if len(parts) > len(subtypes):
        parsed_member.append(' '.join(parts[len(subtypes):]))

    return parsed_member