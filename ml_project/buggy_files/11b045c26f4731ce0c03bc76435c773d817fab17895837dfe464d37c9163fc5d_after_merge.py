    def __query_node_data(vm_, data):
        running = False
        try:
            node = show_instance(vm_['name'], 'action')
            running = (node['state'] == NodeState.RUNNING)
            log.debug(
                'Loaded node data for %s:\nname: %s\nstate: %s',
                vm_['name'],
                pprint.pformat(node['name']),
                node['state']
                )
        except Exception as err:
            log.error(
                'Failed to get nodes list: %s', err,
                # Show the traceback if the debug logging level is enabled
                exc_info_on_loglevel=logging.DEBUG
            )
            # Trigger a failure in the wait for IP function
            return False

        if not running:
            # Still not running, trigger another iteration
            return

        private = node['private_ips']
        public = node['public_ips']

        if private and not public:
            log.warning(
                'Private IPs returned, but not public... Checking for '
                'misidentified IPs'
            )
            for private_ip in private:
                private_ip = preferred_ip(vm_, [private_ip])
                if private_ip is False:
                    continue
                if salt.utils.cloud.is_public_ip(private_ip):
                    log.warning('%s is a public IP', private_ip)
                    data.public_ips.append(private_ip)
                else:
                    log.warning('%s is a private IP', private_ip)
                    if private_ip not in data.private_ips:
                        data.private_ips.append(private_ip)

            if ssh_interface(vm_) == 'private_ips' and data.private_ips:
                return data

        if private:
            data.private_ips = private
            if ssh_interface(vm_) == 'private_ips':
                return data

        if public:
            data.public_ips = public
            if ssh_interface(vm_) != 'private_ips':
                return data

        log.debug('DATA')
        log.debug(data)