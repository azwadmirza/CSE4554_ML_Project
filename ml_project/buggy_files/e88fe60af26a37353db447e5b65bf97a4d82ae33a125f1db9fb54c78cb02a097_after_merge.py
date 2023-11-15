    def setup_entity(self, ext_info, aliased_adapter):
        if "selectable" not in self.__dict__:
            self.selectable = ext_info.selectable

        if set(self.actual_froms).intersection(
            ext_info.selectable._from_objects
        ):
            self.froms.add(ext_info.selectable)