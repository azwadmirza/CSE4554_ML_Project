def _parse_member(settype, member, strict=False):
    subtypes = settype.split(':')[1].split(',')

    all_parts = member.split(' ', 1)
    parts = all_parts[0].split(',')

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

    if len(all_parts) > 1:
        parsed_member.append(all_parts[1])

    return parsed_member