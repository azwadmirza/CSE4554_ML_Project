    def get_all_endpoints(self) -> Generator[Endpoint, None, None]:
        try:
            paths = self.raw_schema["paths"]  # pylint: disable=unsubscriptable-object
            for path, methods in paths.items():
                full_path = self.get_full_path(path)
                if should_skip_endpoint(full_path, self.endpoint):
                    continue
                methods = self.resolve(methods)
                common_parameters = get_common_parameters(methods)
                for method, definition in methods.items():
                    if (
                        method == "parameters"
                        or should_skip_method(method, self.method)
                        or should_skip_by_tag(definition.get("tags"), self.tag)
                    ):
                        continue
                    parameters = itertools.chain(definition.get("parameters", ()), common_parameters)
                    yield self.make_endpoint(full_path, method, parameters, definition)
        except (KeyError, AttributeError, jsonschema.exceptions.RefResolutionError):
            raise InvalidSchema("Schema parsing failed. Please check your schema.")