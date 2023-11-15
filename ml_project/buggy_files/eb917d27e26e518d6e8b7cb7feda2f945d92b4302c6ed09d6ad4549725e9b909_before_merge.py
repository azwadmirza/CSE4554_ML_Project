    def run(self):
        '''
        Run the logic for saltkey
        '''
        if self.opts['gen_keys']:
            salt.crypt.gen_keys(
                    self.opts['gen_keys_dir'],
                    self.opts['gen_keys'],
                    self.opts['keysize'])
            return
        if self.opts['list']:
            self.list_status(self.opts['list'])
        elif self.opts['list_all']:
            self.list_all()
        elif self.opts['print']:
            self.print_key(self.opts['print'])
        elif self.opts['print_all']:
            self.print_all()
        elif self.opts['accept']:
            self.accept(
                self.opts['accept'],
                include_rejected=self.opts['include_all']
            )
        elif self.opts['accept_all']:
            self.accept_all()
        elif self.opts['reject']:
            self.reject(
                self.opts['reject'],
                include_accepted=self.opts['include_all']
            )
        elif self.opts['reject_all']:
            self.reject_all()
        elif self.opts['delete']:
            self.delete(self.opts['delete'])
        elif self.opts['delete_all']:
            self.delete_all()
        elif self.opts['finger']:
            self.finger(self.opts['finger'])
        elif self.opts['finger_all']:
            self.finger_all()
        else:
            self.list_all()