    def _is_module_installed(self, module_spec):
        if self.with_modules:
            module_spec = module_spec.strip()
            module_list, nsv = self.module_base._get_modules(module_spec)
            enabled_streams = self.base._moduleContainer.getEnabledStream(nsv.name)

            if enabled_streams:
                if nsv.stream:
                    if nsv.stream in enabled_streams:
                        return True     # The provided stream was found
                    else:
                        return False    # The provided stream was not found
                else:
                    return True         # No stream provided, but module found

        return False  # seems like a sane default