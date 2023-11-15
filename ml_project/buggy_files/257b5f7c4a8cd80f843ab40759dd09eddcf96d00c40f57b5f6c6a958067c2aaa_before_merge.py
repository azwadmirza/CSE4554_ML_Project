def check_declarative_intent_params(module, want, result):
    failed_conditions = []
    have_neighbors = None
    for w in want:
        want_state = w.get('state')
        want_tx_rate = w.get('tx_rate')
        want_rx_rate = w.get('rx_rate')
        want_neighbors = w.get('neighbors')

        if want_state not in ('up', 'down') and not want_tx_rate and not want_rx_rate and not want_neighbors:
            continue

        if result['changed']:
            sleep(w['delay'])

        command = 'show interfaces %s' % w['name']
        output = run_commands(module, [command])

        if want_state in ('up', 'down'):
            match = re.search(r'%s (\w+)' % 'line protocol is', output[0], re.M)
            have_state = None
            if match:
                have_state = match.group(1)
            if have_state is None or not conditional(want_state, have_state.strip()):
                failed_conditions.append('state ' + 'eq(%s)' % want_state)

        if want_tx_rate:
            match = re.search(r'%s (\d+)' % 'output rate', output[0], re.M)
            have_tx_rate = None
            if match:
                have_tx_rate = match.group(1)

            if have_tx_rate is None or not conditional(want_tx_rate, have_tx_rate.strip(), cast=int):
                failed_conditions.append('tx_rate ' + want_tx_rate)

        if want_rx_rate:
            match = re.search(r'%s (\d+)' % 'input rate', output[0], re.M)
            have_rx_rate = None
            if match:
                have_rx_rate = match.group(1)

            if have_rx_rate is None or not conditional(want_rx_rate, have_rx_rate.strip(), cast=int):
                failed_conditions.append('rx_rate ' + want_rx_rate)

        if want_neighbors:
            have_host = []
            have_port = []
            if have_neighbors is None:
                have_neighbors = run_commands(module, ['show lldp neighbors {}'.format(w['name'])])

            if have_neighbors[0]:
                lines = have_neighbors[0].strip().split('\n')
                col = None
                for index, line in enumerate(lines):
                    if re.search(r"^Port\s+Neighbor Device ID\s+Neighbor Port ID\s+TTL", line):
                        col = index
                        break

                if col and col < len(lines) - 1:
                    for items in lines[col + 1:]:
                        value = re.split(r'\s+', items)
                        try:
                            have_port.append(value[2])
                            have_host.append(value[1])
                        except IndexError:
                            pass

            for item in want_neighbors:
                host = item.get('host')
                port = item.get('port')
                if host and host not in have_host:
                    failed_conditions.append('host ' + host)
                if port and port not in have_port:
                    failed_conditions.append('port ' + port)
    return failed_conditions