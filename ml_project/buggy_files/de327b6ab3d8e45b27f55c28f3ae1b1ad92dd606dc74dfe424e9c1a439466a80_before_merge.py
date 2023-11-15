    def parse(
        self, with_import: Optional[bool] = True, format_: Optional[bool] = True
    ) -> Union[str, Dict[Tuple[str, ...], str]]:

        self.parse_raw()

        if with_import:
            if self.target_python_version == PythonVersion.PY_37:
                self.imports.append(IMPORT_ANNOTATIONS)

        _, sorted_data_models, require_update_action_models = sort_data_models(
            self.results
        )

        results: Dict[Tuple[str, ...], str] = {}

        module_key = lambda x: (*x.name.split('.')[:-1],)

        # process in reverse order to correctly establish module levels
        grouped_models = groupby(
            sorted(sorted_data_models.values(), key=module_key, reverse=True),
            key=module_key,
        )
        for module, models in ((k, [*v]) for k, v in grouped_models):
            module_path = '.'.join(module)

            init = False
            if module:
                parent = (*module[:-1], '__init__.py')
                if parent not in results:
                    results[parent] = ''
                if (*module, '__init__.py') in results:
                    module = (*module, '__init__.py')
                    init = True
                else:
                    module = (*module[:-1], f'{module[-1]}.py')
            else:
                module = ('__init__.py',)

            result: List[str] = []
            imports = Imports()
            models_to_update: List[str] = []

            for model in models:
                used_import_names: Set[str] = set()
                alias_map: Dict[str, str] = {}
                if model.name in require_update_action_models:
                    models_to_update += [model.name]
                imports.append(model.imports)
                for field in model.fields:
                    type_hint = field.type_hint
                    if type_hint is None:  # pragma: no cover
                        continue
                    for data_type in field.data_types:
                        if '.' not in data_type.type:
                            continue
                        from_, import_ = relative(module_path, data_type.type)
                        alias = get_uniq_name(import_, used_import_names)
                        used_import_names.add(import_)
                        if alias != import_:
                            alias_map[f'{from_}/{import_}'] = alias
                        name = data_type.type.rsplit('.', 1)[-1]
                        pattern = re.compile(rf'\b{re.escape(data_type.type)}\b')
                        if from_ and import_:
                            type_hint = pattern.sub(rf'{alias}.{name}', type_hint)
                        else:
                            type_hint = pattern.sub(name, type_hint)

                    field.type_hint = type_hint

                for ref_name in model.reference_classes:
                    from_, import_ = relative(module_path, ref_name)
                    if init:
                        from_ += "."
                    if from_ and import_:
                        imports.append(
                            Import(
                                from_=from_,
                                import_=import_,
                                alias=alias_map.get(f'{from_}/{import_}'),
                            )
                        )

            if with_import:
                result += [imports.dump(), self.imports.dump(), '\n']

            code = dump_templates(models)
            result += [code]

            if self.dump_resolve_reference_action is not None:
                result += ['\n', self.dump_resolve_reference_action(models_to_update)]

            body = '\n'.join(result)
            if format_:
                body = format_code(body, self.target_python_version)

            results[module] = body

        # retain existing behaviour
        if [*results] == [('__init__.py',)]:
            return results[('__init__.py',)]

        return results