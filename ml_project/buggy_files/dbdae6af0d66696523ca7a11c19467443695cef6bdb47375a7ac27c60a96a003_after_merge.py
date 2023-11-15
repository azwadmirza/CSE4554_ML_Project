    def validate_domain_yaml(cls, yaml):
        """Validate domain yaml."""
        from pykwalify.core import Core

        log = logging.getLogger("pykwalify")
        log.setLevel(logging.WARN)

        try:
            schema_file = pkg_resources.resource_filename(
                __name__, "schemas/domain.yml"
            )
            source_data = rasa.utils.io.read_yaml(yaml)
        except YAMLError:
            raise InvalidDomain(
                "The provided domain file is invalid. You can use "
                "http://www.yamllint.com/ to validate the yaml syntax "
                "of your domain file."
            )
        except DuplicateKeyError as e:
            raise InvalidDomain(
                "The provided domain file contains a duplicated key: {}".format(str(e))
            )

        try:
            c = Core(source_data=source_data, schema_files=[schema_file])
            c.validate(raise_exception=True)
        except SchemaError:
            raise InvalidDomain(
                "Failed to validate your domain yaml. "
                "Please make sure the file is correct; to do so, "
                "take a look at the errors logged during "
                "validation previous to this exception. "
                "You can also validate your domain file's yaml "
                "syntax using http://www.yamllint.com/."
            )