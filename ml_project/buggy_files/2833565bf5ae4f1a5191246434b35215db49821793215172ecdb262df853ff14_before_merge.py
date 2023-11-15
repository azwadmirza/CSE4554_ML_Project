    def set_config(self, config: Type['BaseConfig']) -> None:
        self.model_config = config
        info_from_config = config.get_field_info(self.name)
        config.prepare_field(self)
        if info_from_config:
            self.field_info.alias = info_from_config.get('alias') or self.field_info.alias or self.name
            self.alias = cast(str, self.field_info.alias)