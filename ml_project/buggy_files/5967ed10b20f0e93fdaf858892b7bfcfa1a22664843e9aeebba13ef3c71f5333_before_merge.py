    def _load_reporter(self):
        name = self._reporter_name.lower()
        if name in self._reporters:
            self.set_reporter(self._reporters[name]())
        else:
            qname = self._reporter_name
            module = modutils.load_module_from_name(
                modutils.get_module_part(qname))
            class_name = qname.split('.')[-1]
            reporter_class = getattr(module, class_name)
            self.set_reporter(reporter_class())