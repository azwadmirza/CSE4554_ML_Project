    def check_declarative_intent_params(self):
        failed_conditions = []
        for want_item in self._want:
            want_state = want_item.get('state')
            want_tx_rate = want_item.get('tx_rate')
            want_rx_rate = want_item.get('rx_rate')
            if want_state not in ('up', 'down') and not want_tx_rate and not want_rx_rate:
                continue

            if self._result['changed']:
                sleep(want_item['delay'])

            command = 'show interfaces {!s}'.format(want_item['name'])
            out = run_command(self._module, command)[0]

            if want_state in ('up', 'down'):
                match = re.search(r'%s (\w+)' % 'line protocol is', out, re.M)
                have_state = None
                if match:
                    have_state = match.group(1)
                    if have_state.strip() == 'administratively':
                        match = re.search(r'%s (\w+)' % 'administratively', out, re.M)
                        if match:
                            have_state = match.group(1)

                if have_state is None or not conditional(want_state, have_state.strip()):
                    failed_conditions.append('state ' + 'eq({!s})'.format(want_state))

            if want_tx_rate:
                match = re.search(r'%s (\d+)' % 'output rate', out, re.M)
                have_tx_rate = None
                if match:
                    have_tx_rate = match.group(1)

                if have_tx_rate is None or not conditional(want_tx_rate, have_tx_rate.strip(), cast=int):
                    failed_conditions.append('tx_rate ' + want_tx_rate)

            if want_rx_rate:
                match = re.search(r'%s (\d+)' % 'input rate', out, re.M)
                have_rx_rate = None
                if match:
                    have_rx_rate = match.group(1)

                if have_rx_rate is None or not conditional(want_rx_rate, have_rx_rate.strip(), cast=int):
                    failed_conditions.append('rx_rate ' + want_rx_rate)

        if failed_conditions:
            msg = 'One or more conditional statements have not been satisfied'
            self._module.fail_json(msg=msg, failed_conditions=failed_conditions)