    def resolve_extends(self, service_dict):
        if 'extends' not in service_dict:
            return service_dict

        extends_options = self.validate_extends_options(service_dict['name'], service_dict['extends'])

        if self.working_dir is None:
            raise Exception("No working_dir passed to ServiceLoader()")

        if 'file' in extends_options:
            extends_from_filename = extends_options['file']
            other_config_path = expand_path(self.working_dir, extends_from_filename)
        else:
            other_config_path = self.filename

        other_working_dir = os.path.dirname(other_config_path)
        other_already_seen = self.already_seen + [self.signature(service_dict['name'])]
        other_loader = ServiceLoader(
            working_dir=other_working_dir,
            filename=other_config_path,
            already_seen=other_already_seen,
        )

        other_config = load_yaml(other_config_path)
        other_service_dict = other_config[extends_options['service']]
        other_loader.detect_cycle(extends_options['service'])
        other_service_dict = other_loader.make_service_dict(
            service_dict['name'],
            other_service_dict,
        )
        validate_extended_service_dict(
            other_service_dict,
            filename=other_config_path,
            service=extends_options['service'],
        )

        return merge_service_dicts(other_service_dict, service_dict)