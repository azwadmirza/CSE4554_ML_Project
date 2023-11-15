    def load_callbacks(self):
        '''
        Loads all available callbacks, with the exception of those which
        utilize the CALLBACK_TYPE option. When CALLBACK_TYPE is set to 'stdout',
        only one such callback plugin will be loaded.
        '''

        if self._callbacks_loaded:
            return

        stdout_callback_loaded = False
        if self._stdout_callback is None:
            self._stdout_callback = C.DEFAULT_STDOUT_CALLBACK

        if isinstance(self._stdout_callback, CallbackBase):
            stdout_callback_loaded = True
        elif isinstance(self._stdout_callback, string_types):
            if self._stdout_callback not in callback_loader:
                raise AnsibleError("Invalid callback for stdout specified: %s" % self._stdout_callback)
            else:
                self._stdout_callback = callback_loader.get(self._stdout_callback)
                self._stdout_callback.set_options()
                stdout_callback_loaded = True
        else:
            raise AnsibleError("callback must be an instance of CallbackBase or the name of a callback plugin")

        for callback_plugin in callback_loader.all(class_only=True):
            callback_type = getattr(callback_plugin, 'CALLBACK_TYPE', '')
            callback_needs_whitelist = getattr(callback_plugin, 'CALLBACK_NEEDS_WHITELIST', False)
            (callback_name, _) = os.path.splitext(os.path.basename(callback_plugin._original_path))
            if callback_type == 'stdout':
                # we only allow one callback of type 'stdout' to be loaded,
                if callback_name != self._stdout_callback or stdout_callback_loaded:
                    continue
                stdout_callback_loaded = True
            elif callback_name == 'tree' and self._run_tree:
                # special case for ansible cli option
                pass
            elif not self._run_additional_callbacks or (callback_needs_whitelist and (
                    C.DEFAULT_CALLBACK_WHITELIST is None or callback_name not in C.DEFAULT_CALLBACK_WHITELIST)):
                # 2.x plugins shipped with ansible should require whitelisting, older or non shipped should load automatically
                continue

            callback_obj = callback_plugin()
            callback_obj.set_options()
            self._callback_plugins.append(callback_obj)

        for callback_plugin_name in (c for c in C.DEFAULT_CALLBACK_WHITELIST if AnsibleCollectionRef.is_valid_fqcr(c)):
            # TODO: need to extend/duplicate the stdout callback check here (and possible move this ahead of the old way
            callback_obj = callback_loader.get(callback_plugin_name)
            if callback_obj:
                callback_obj.set_options()
                self._callback_plugins.append(callback_obj)
            else:
                display.warning("Skipping '%s', unable to load or use as a callback" % callback_plugin_name)

        self._callbacks_loaded = True