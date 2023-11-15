    def _is_module_installed(self, module_spec):
        if self.with_modules:
            module_spec = module_spec.strip()
            module_list, nsv = self.module_base._get_modules(module_spec)

            if nsv.stream in self.base._moduleContainer.getEnabledStream(nsv.name):
                return True

        return False  # seems like a sane default