    def get_endpoint_by_reference(self, reference: str) -> Endpoint:
        """Get local or external `Endpoint` instance by reference.

        Reference example: #/paths/~1users~1{user_id}/patch
        """
        scope, data = self.resolver.resolve(reference)
        path, method = scope.rsplit("/", maxsplit=2)[-2:]
        path = path.replace("~1", "/").replace("~0", "~")
        full_path = self.get_full_path(path)
        resolved_definition = self.resolver.resolve_all(data)
        parent_ref, _ = reference.rsplit("/", maxsplit=1)
        _, methods = self.resolver.resolve(parent_ref)
        common_parameters = get_common_parameters(methods)
        parameters = itertools.chain(resolved_definition.get("parameters", ()), common_parameters)
        raw_definition = EndpointDefinition(data, resolved_definition, scope)
        return self.make_endpoint(full_path, method, parameters, resolved_definition, raw_definition)