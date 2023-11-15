    def refresh_namespacebrowser(self, interrupt=False):
        """Refresh namespace browser"""
        if self.kernel_client is None:
            return
        if self.namespacebrowser:
            self.call_kernel(
                interrupt=interrupt,
                callback=self.set_namespace_view
            ).get_namespace_view()
            self.call_kernel(
                interrupt=interrupt,
                callback=self.set_var_properties
            ).get_var_properties()