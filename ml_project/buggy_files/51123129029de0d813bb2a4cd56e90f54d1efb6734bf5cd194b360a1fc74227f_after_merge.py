    def handle_key_cache(self):
        '''
        Evaluate accepted keys and create a msgpack file
        which contains a list
        '''
        if self.opts['key_cache'] == 'sched':
            keys = []
            #TODO DRY from CKMinions
            if self.opts['transport'] in ('zeromq', 'tcp'):
                acc = 'minions'
            else:
                acc = 'accepted'

            for fn_ in os.listdir(os.path.join(self.opts['pki_dir'], acc)):
                if not fn_.startswith('.') and os.path.isfile(os.path.join(self.opts['pki_dir'], acc, fn_)):
                    keys.append(fn_)
            log.debug('Writing master key cache')
            # Write a temporary file securely
            if six.PY2:
                with salt.utils.atomicfile.atomic_open(os.path.join(self.opts['pki_dir'], acc, '.key_cache')) as cache_file:
                    self.serial.dump(keys, cache_file)
            else:
                with salt.utils.atomicfile.atomic_open(os.path.join(self.opts['pki_dir'], acc, '.key_cache'), mode='wb') as cache_file:
                    self.serial.dump(keys, cache_file)