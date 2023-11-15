    def get_base_args(self):
        # get ansible-inventory absolute path for running in bubblewrap/proot, in Popen
        abs_ansible_inventory = shutil.which('ansible-inventory')
        bargs= [abs_ansible_inventory, '-i', self.source]
        logger.debug('Using base command: {}'.format(' '.join(bargs)))
        return bargs