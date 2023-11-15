    def select_device(self, plugin: 'HW_PluginBase', handler,
                      keystore: 'Hardware_KeyStore', devices=None) -> 'DeviceInfo':
        '''Ask the user to select a device to use if there is more than one,
        and return the DeviceInfo for the device.'''
        while True:
            infos = self.unpaired_device_infos(handler, plugin, devices)
            if infos:
                break
            msg = _('Please insert your {}').format(plugin.device)
            if keystore.label:
                msg += ' ({})'.format(keystore.label)
            msg += '. {}\n\n{}'.format(
                _('Verify the cable is connected and that '
                  'no other application is using it.'),
                _('Try to connect again?')
            )
            if not handler.yes_no_question(msg):
                raise UserCancelled()
            devices = None
        if len(infos) == 1:
            return infos[0]
        # select device by label
        for info in infos:
            if info.label == keystore.label:
                return info
        msg = _("Please select which {} device to use:").format(plugin.device)
        descriptions = [str(info.label) + ' (%s)'%(_("initialized") if info.initialized else _("wiped")) for info in infos]
        c = handler.query_choice(msg, descriptions)
        if c is None:
            raise UserCancelled()
        info = infos[c]
        # save new label
        keystore.set_label(info.label)
        if handler.win.wallet is not None:
            handler.win.wallet.save_keystore()
        return info