    def parse_ref(self, obj: JsonSchemaObject) -> None:
        if obj.ref:
            ref: str = obj.ref
            # https://swagger.io/docs/specification/using-ref/
            if obj.ref.startswith('#'):
                # Local Reference – $ref: '#/definitions/myElement'
                pass
            elif '://' in ref:
                # URL Reference – $ref: 'http://path/to/your/resource' Uses the whole document located on the different server.
                raise NotImplementedError(f'URL Reference is not supported. $ref:{ref}')

            else:
                # Remote Reference – $ref: 'document.json' Uses the whole document located on the same server and in the same location.
                # TODO treat edge case
                relative_path, object_path = ref.split('#/')
                full_path = self.base_path / relative_path
                with full_path.open() as f:
                    if full_path.suffix.lower() == '.json':
                        import json

                        ref_body: Dict[str, Any] = json.load(f)
                    else:
                        # expect yaml
                        import yaml

                        ref_body = yaml.safe_load(f)
                    object_parents = object_path.split('/')
                    ref_path = str(full_path) + '#/' + object_path
                    if ref_path not in self.excludes_ref_path:
                        self.excludes_ref_path.add(str(full_path) + '#/' + object_path)
                        model = get_model_by_path(ref_body, object_parents)
                        self.parse_raw_obj(object_parents[-1], model)

        if obj.items:
            if isinstance(obj.items, JsonSchemaObject):
                self.parse_ref(obj.items)
            else:
                for item in obj.items:
                    self.parse_ref(item)
        if isinstance(obj.additionalProperties, JsonSchemaObject):
            self.parse_ref(obj.additionalProperties)
        for item in obj.anyOf:
            self.parse_ref(item)
        for item in obj.allOf:
            self.parse_ref(item)
        if obj.properties:
            for value in obj.properties.values():
                self.parse_ref(value)