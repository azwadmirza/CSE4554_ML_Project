    def get_base_args(self):
        # get ansible-inventory absolute path for running in bubblewrap/proot, in Popen
        bargs= [self.get_path_to_ansible_inventory(), '-i', self.source]
        logger.debug('Using base command: {}'.format(' '.join(bargs)))
        return bargs