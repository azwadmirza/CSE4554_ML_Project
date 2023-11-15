    def send_callback(self, method_name, *args, **kwargs):
        for callback_plugin in [self._stdout_callback] + self._callback_plugins:
            # a plugin that set self.disabled to True will not be called
            # see osx_say.py example for such a plugin
            if getattr(callback_plugin, 'disabled', False):
                continue
            methods = [
                getattr(callback_plugin, method_name, None),
                getattr(callback_plugin, 'v2_on_any', None)
            ]
            for method in methods:
                if method is not None:
                    try:
                        # temporary hack, required due to a change in the callback API, so
                        # we don't break backwards compatibility with callbacks which were
                        # designed to use the original API
                        # FIXME: target for removal and revert to the original code here
                        #        after a year (2017-01-14)
                        if method_name == 'v2_playbook_on_start':
                            import inspect
                            (f_args, f_varargs, f_keywords, f_defaults) = inspect.getargspec(method)
                            if 'playbook' in f_args:
                                method(*args, **kwargs)
                            else:
                                method()
                        else:
                            method(*args, **kwargs)
                    except Exception as e:
                        import traceback
                        orig_tb = to_unicode(traceback.format_exc())
                        try:
                            v1_method = method.replace('v2_','')
                            v1_method(*args, **kwargs)
                        except Exception:
                            if display.verbosity >= 3:
                                display.warning(orig_tb, formatted=True)
                            else:
                                display.warning('Error when using %s: %s' % (method, str(e)))