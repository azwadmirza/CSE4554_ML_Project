    def register_view(self, view):
        """ register_view will create the needed structure
        in order to be able to sent all data to Prometheus
        """
        v_name = get_view_name(self.options.namespace, view)

        if v_name not in self.registered_views:
            desc = {'name': v_name,
                    'documentation': view.description,
                    'labels': list(view.columns)}
            self.registered_views[v_name] = desc
            self.registry.register(self)