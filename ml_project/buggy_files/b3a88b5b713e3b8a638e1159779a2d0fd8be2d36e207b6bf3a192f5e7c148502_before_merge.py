    def parse_models_entry(self, model_dict, path, package_name, root_dir):
        model_name = model_dict['name']
        refs = ParserRef()
        for column in model_dict.get('columns', []):
            column_tests = self._parse_column(model_dict, column, package_name,
                                              root_dir, path, refs)
            for node in column_tests:
                yield 'test', node

        for test in model_dict.get('tests', []):
            try:
                node = self.build_test_node(model_dict, package_name, test,
                                            root_dir, path)
            except dbt.exceptions.CompilationException as exc:
                dbt.exceptions.warn_or_error(
                    'in {}: {}'.format(path, exc.msg), test
                )
                continue
            yield 'test', node

        context = {'doc': dbt.context.parser.docs(model_dict, refs.docrefs)}
        description = model_dict.get('description', '')
        get_rendered(description, context)

        patch = ParsedNodePatch(
            name=model_name,
            original_file_path=path,
            description=description,
            columns=refs.column_info,
            docrefs=refs.docrefs
        )
        yield 'patch', patch