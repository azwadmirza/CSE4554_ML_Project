    def validate_and_construct_extends(self):
        extends = self.service_dict['extends']
        if not isinstance(extends, dict):
            extends = {'service': extends}

        validate_extends_file_path(
            self.service_name,
            extends,
            self.filename
        )
        self.extended_config_path = self.get_extended_config_path(
            extends
        )
        self.extended_service_name = extends['service']

        full_extended_config = pre_process_config(
            load_yaml(self.extended_config_path)
        )

        validate_extended_service_exists(
            self.extended_service_name,
            full_extended_config,
            self.extended_config_path
        )
        validate_against_fields_schema(full_extended_config)

        self.extended_config = full_extended_config[self.extended_service_name]