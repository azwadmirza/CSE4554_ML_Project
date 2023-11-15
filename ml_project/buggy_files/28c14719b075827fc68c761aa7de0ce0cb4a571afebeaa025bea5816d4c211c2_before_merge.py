    def reconcile_procs(self, running):
        '''
        Check the running dict for processes and resolve them
        '''
        retset = set()
        for tag in running:
            proc = running[tag].get('proc')
            if proc:
                if not proc.is_alive():
                    ret_cache = os.path.join(self.opts['cachedir'], self.jid, _clean_tag(tag))
                    if not os.path.isfile(ret_cache):
                        ret = {'result': False,
                               'comment': 'Parallel process failed to return',
                               'name': running[tag]['name'],
                               'changes': {}}
                    try:
                        with salt.utils.fopen(ret_cache, 'rb') as fp_:
                            ret = msgpack_deserialize(fp_.read())
                    except (OSError, IOError):
                        ret = {'result': False,
                               'comment': 'Parallel cache failure',
                               'name': running[tag]['name'],
                               'changes': {}}
                    running[tag].update(ret)
                    running[tag].pop('proc')
                else:
                    retset.add(False)
        return False not in retset