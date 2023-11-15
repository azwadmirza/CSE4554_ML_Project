    def _group_endpoints_by_operation_id(self) -> Generator[Tuple[str, Endpoint], None, None]:
        for path, methods in self.raw_schema["paths"].items():
            full_path = self.get_full_path(path)
            scope, raw_methods = self._resolve_methods(methods)
            methods = self.resolver.resolve_all(methods)
            common_parameters = get_common_parameters(methods)
            for method, resolved_definition in methods.items():
                if method not in self.operations or "operationId" not in resolved_definition:
                    continue
                parameters = itertools.chain(resolved_definition.get("parameters", ()), common_parameters)
                raw_definition = EndpointDefinition(raw_methods[method], scope)
                yield resolved_definition["operationId"], self.make_endpoint(
                    full_path, method, parameters, resolved_definition, raw_definition
                )