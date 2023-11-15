    def on_device(self, name, device_info: 'DeviceInfo', *, purpose, storage=None):
        self.plugin = self.plugins.get_plugin(name)
        assert isinstance(self.plugin, HW_PluginBase)
        devmgr = self.plugins.device_manager
        try:
            self.plugin.setup_device(device_info, self, purpose)
        except OSError as e:
            self.show_error(_('We encountered an error while connecting to your device:')
                            + '\n' + str(e) + '\n'
                            + _('To try to fix this, we will now re-pair with your device.') + '\n'
                            + _('Please try again.'))
            devmgr.unpair_id(device_info.device.id_)
            self.choose_hw_device(purpose, storage=storage)
            return
        except OutdatedHwFirmwareException as e:
            if self.question(e.text_ignore_old_fw_and_continue(), title=_("Outdated device firmware")):
                self.plugin.set_ignore_outdated_fw()
                # will need to re-pair
                devmgr.unpair_id(device_info.device.id_)
            self.choose_hw_device(purpose, storage=storage)
            return
        except (UserCancelled, GoBack):
            self.choose_hw_device(purpose, storage=storage)
            return
        except BaseException as e:
            self.logger.exception('')
            self.show_error(str(e))
            self.choose_hw_device(purpose, storage=storage)
            return
        if purpose == HWD_SETUP_NEW_WALLET:
            def f(derivation, script_type):
                derivation = normalize_bip32_derivation(derivation)
                self.run('on_hw_derivation', name, device_info, derivation, script_type)
            self.derivation_and_script_type_dialog(f)
        elif purpose == HWD_SETUP_DECRYPT_WALLET:
            client = devmgr.client_by_id(device_info.device.id_)
            password = client.get_password_for_storage_encryption()
            try:
                storage.decrypt(password)
            except InvalidPassword:
                # try to clear session so that user can type another passphrase
                client = devmgr.client_by_id(device_info.device.id_)
                if hasattr(client, 'clear_session'):  # FIXME not all hw wallet plugins have this
                    client.clear_session()
                raise
        else:
            raise Exception('unknown purpose: %s' % purpose)