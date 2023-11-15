def jobber_check(self):
    '''
    Iterate over the shell jobbers and return the ones that have finished
    '''
    rms = []
    for jid in self.shells.value:
        if isinstance(self.shells.value[jid]['proc'].poll(), int):
            rms.append(jid)
            data = self.shells.value[jid]
            stdout, stderr = data['proc'].communicate()
            ret = salt.utils.json.loads(stdout, object_hook=salt.utils.data.encode_dict)['local']
            route = {'src': (self.stack.value.local.name, 'manor', 'jid_ret'),
                     'dst': (data['msg']['route']['src'][0], None, 'remote_cmd')}
            ret['cmd'] = '_return'
            ret['id'] = self.opts.value['id']
            ret['jid'] = jid
            msg = {'route': route, 'load': ret}
            master = self.stack.value.nameRemotes.get(data['msg']['route']['src'][0])
            self.stack.value.message(
                    msg,
                    master.uid)
    for rm_ in rms:
        self.shells.value.pop(rm_)