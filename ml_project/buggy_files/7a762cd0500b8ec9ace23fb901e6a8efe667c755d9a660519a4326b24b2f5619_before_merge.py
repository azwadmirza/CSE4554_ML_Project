    def __query_node_data(vm_, data, floating):
        try:
            node = show_instance(vm_['name'], 'action')
            log.debug(
                'Loaded node data for {0}:\n{1}'.format(
                    vm_['name'],
                    pprint.pformat(node)
                )
            )
        except Exception as err:
            log.error(
                'Failed to get nodes list: {0}'.format(
                    err
                ),
                # Show the traceback if the debug logging level is enabled
                exc_info_on_loglevel=logging.DEBUG
            )
            # Trigger a failure in the wait for IP function
            return False

        running = node['state'] == NodeState.RUNNING
        if not running:
            # Still not running, trigger another iteration
            return

        if rackconnect(vm_) is True:
            check_libcloud_version((0, 14, 0), why='rackconnect: True')
            extra = node.get('extra')
            rc_status = extra.get('metadata', {}).get(
                'rackconnect_automation_status', '')
            access_ip = extra.get('access_ip', '')

            if rc_status != 'DEPLOYED':
                log.debug('Waiting for Rackconnect automation to complete')
                return

        if managedcloud(vm_) is True:
            extra = node.get('extra')
            mc_status = extra.get('metadata', {}).get(
                'rax_service_level_automation', '')

            if mc_status != 'Complete':
                log.debug('Waiting for managed cloud automation to complete')
                return

        public = node['public_ips']
        if floating:
            try:
                name = data.name
                ip = floating[0].ip_address
                conn.ex_attach_floating_ip_to_node(data, ip)
                log.info(
                    'Attaching floating IP \'{0}\' to node \'{1}\''.format(
                        ip, name
                    )
                )
                data.public_ips.append(ip)
                public = data.public_ips
            except Exception:
                # Note(pabelanger): Because we loop, we only want to attach the
                # floating IP address one. So, expect failures if the IP is
                # already attached.
                pass

        result = []
        private = node['private_ips']
        if private and not public:
            log.warn(
                'Private IPs returned, but not public... Checking for '
                'misidentified IPs'
            )
            for private_ip in private:
                private_ip = preferred_ip(vm_, [private_ip])
                if salt.utils.cloud.is_public_ip(private_ip):
                    log.warn('{0} is a public IP'.format(private_ip))
                    data.public_ips.append(private_ip)
                    log.warn(
                        'Public IP address was not ready when we last checked.'
                        ' Appending public IP address now.'
                    )
                    public = data.public_ips
                else:
                    log.warn('{0} is a private IP'.format(private_ip))
                    ignore_ip = ignore_cidr(vm_, private_ip)
                    if private_ip not in data.private_ips and not ignore_ip:
                        result.append(private_ip)

        if rackconnect(vm_) is True and ssh_interface(vm_) != 'private_ips':
            data.public_ips = access_ip
            return data

        # populate return data with private_ips
        # when ssh_interface is set to private_ips and public_ips exist
        if not result and ssh_interface(vm_) == 'private_ips':
            for private_ip in private:
                ignore_ip = ignore_cidr(vm_, private_ip)
                if private_ip not in data.private_ips and not ignore_ip:
                    result.append(private_ip)

        if result:
            log.debug('result = {0}'.format(result))
            data.private_ips = result
            if ssh_interface(vm_) == 'private_ips':
                return data

        if public:
            data.public_ips = public
            if ssh_interface(vm_) != 'private_ips':
                return data