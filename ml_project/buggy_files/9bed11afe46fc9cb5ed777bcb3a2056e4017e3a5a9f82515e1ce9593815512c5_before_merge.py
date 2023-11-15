    def select_device(self, plugin: 'HW_PluginBase', handler: 'HardwareHandlerBase',
                      keystore: 'Hardware_KeyStore', devices: List['Device'] = None) -> 'DeviceInfo':
        '''Ask the user to select a device to use if there is more than one,
        and return the DeviceInfo for the device.'''
        # ideally this should not be called from the GUI thread...
        # assert handler.get_gui_thread() != threading.current_thread(), 'must not be called from GUI thread'
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
        # select device by label automatically;
        # but only if not a placeholder label and only if there is no collision
        device_labels = [info.label for info in infos]
        if (keystore.label not in PLACEHOLDER_HW_CLIENT_LABELS
                and device_labels.count(keystore.label) == 1):
            for info in infos:
                if info.label == keystore.label:
                    return info
        # ask user to select device
        msg = _("Please select which {} device to use:").format(plugin.device)
        descriptions = ["{label} ({init}, {transport})"
                        .format(label=info.label or _("An unnamed {}").format(info.plugin_name),
                                init=(_("initialized") if info.initialized else _("wiped")),
                                transport=info.device.transport_ui_string)
                        for info in infos]
        c = handler.query_choice(msg, descriptions)
        if c is None:
            raise UserCancelled()
        info = infos[c]
        # save new label
        keystore.set_label(info.label)
        wallet = handler.get_wallet()
        if wallet is not None:
            wallet.save_keystore()
        return info