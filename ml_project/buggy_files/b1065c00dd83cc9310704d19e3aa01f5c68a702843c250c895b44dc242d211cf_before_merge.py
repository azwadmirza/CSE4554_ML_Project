    def create(self):
        if self.can_be_inline:
            self.create_inline()
        else:
            self.create_via_sub_process()
            # TODO: cleanup activation scripts
        if self.builtin_way is not None:
            for site_package in self.builtin_way.site_packages:
                ensure_dir(site_package)