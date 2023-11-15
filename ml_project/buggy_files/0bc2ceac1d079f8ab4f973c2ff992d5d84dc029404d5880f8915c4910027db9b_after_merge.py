    def process(self, network_addrs):
        client = local_session(self.manager.session_factory).client('ec2')
        force = self.data.get('force')
        assoc_addrs = [addr for addr in network_addrs if 'AssociationId' in addr]
        unassoc_addrs = [addr for addr in network_addrs if 'AssociationId' not in addr]

        if len(assoc_addrs) and not force:
            self.log.warning(
                "Filtered %d attached eips of %d eips. Use 'force: true' to release them.",
                len(assoc_addrs), len(network_addrs))
        elif len(assoc_addrs) and force:
            unassoc_addrs = itertools.chain(
                unassoc_addrs, self.process_attached(client, assoc_addrs))

        for r in unassoc_addrs:
            try:
                client.release_address(AllocationId=r['AllocationId'])
            except ClientError as e:
                # If its already been released, ignore, else raise.
                if e.response['Error']['Code'] == 'InvalidAllocationID.NotFound':
                    raise