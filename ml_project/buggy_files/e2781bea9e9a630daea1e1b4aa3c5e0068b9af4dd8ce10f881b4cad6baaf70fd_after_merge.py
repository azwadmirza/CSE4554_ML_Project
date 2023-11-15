    def execute_macro(
        self,
        macro_name: str,
        manifest: Optional[Manifest] = None,
        project: Optional[str] = None,
        context_override: Optional[Dict[str, Any]] = None,
        kwargs: Dict[str, Any] = None,
        release: bool = False,
        text_only_columns: Optional[Iterable[str]] = None,
    ) -> agate.Table:
        """Look macro_name up in the manifest and execute its results.

        :param macro_name: The name of the macro to execute.
        :param manifest: The manifest to use for generating the base macro
            execution context. If none is provided, use the internal manifest.
        :param project: The name of the project to search in, or None for the
            first match.
        :param context_override: An optional dict to update() the macro
            execution context.
        :param kwargs: An optional dict of keyword args used to pass to the
            macro.
        :param release: If True, release the connection after executing.
        """
        if kwargs is None:
            kwargs = {}
        if context_override is None:
            context_override = {}

        if manifest is None:
            manifest = self._internal_manifest

        macro = manifest.find_macro_by_name(
            macro_name, self.config.project_name, project
        )
        if macro is None:
            if project is None:
                package_name = 'any package'
            else:
                package_name = 'the "{}" package'.format(project)

            raise RuntimeException(
                'dbt could not find a macro with the name "{}" in {}'
                .format(macro_name, package_name)
            )
        # This causes a reference cycle, as generate_runtime_macro()
        # ends up calling get_adapter, so the import has to be here.
        from dbt.context.providers import generate_runtime_macro
        macro_context = generate_runtime_macro(
            macro=macro,
            config=self.config,
            manifest=manifest,
            package_name=project
        )
        macro_context.update(context_override)

        macro_function = MacroGenerator(macro, macro_context)

        with self.connections.exception_handler(f'macro {macro_name}'):
            try:
                result = macro_function(**kwargs)
            finally:
                if release:
                    self.release_connection()
        return result