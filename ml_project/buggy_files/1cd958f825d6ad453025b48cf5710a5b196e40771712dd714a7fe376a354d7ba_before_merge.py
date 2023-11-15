    def _parse_column(self, target, column, package_name, root_dir, path,
                      refs):
        # this should yield ParsedNodes where resource_type == NodeType.Test
        column_name = column['name']
        description = column.get('description', '')

        refs.add(column_name, description)
        context = {
            'doc': dbt.context.parser.docs(target, refs.docrefs, column_name)
        }
        get_rendered(description, context)

        for test in column.get('tests', []):
            try:
                yield self.build_test_node(
                    target, package_name, test, root_dir,
                    path, column_name
                )
            except dbt.exceptions.CompilationException as exc:
                dbt.exceptions.warn_or_error(
                    'in {}: {}'.format(path, exc.msg), None
                )
                continue