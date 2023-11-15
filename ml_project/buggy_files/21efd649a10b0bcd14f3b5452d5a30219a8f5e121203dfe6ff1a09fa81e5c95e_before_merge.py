    def _set_log_item(self, item, name=None):
        # Pathlib compatibility
        if isinstance(item, Path):
            item = str(item)
        if isinstance(item, str) or callable(item):
            if not callable(item):
                item = self.apply_default_remote(item)
                item = self._update_item_wildcard_constraints(item)

            self.log.append(IOFile(item, rule=self) if isinstance(item, str) else item)
            if name:
                self.log.add_name(name)
        else:
            try:
                start = len(self.log)
                for i in item:
                    self._set_log_item(i)
                if name:
                    self.log.set_name(name, start, end=len(self.log))
            except TypeError:
                raise SyntaxError("Log files have to be specified as strings.")