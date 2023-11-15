    def load_file(filename, config):
        processed_config = pre_process_config(config)
        validate_against_fields_schema(processed_config)
        return [
            build_service(filename, name, service_config)
            for name, service_config in processed_config.items()
        ]