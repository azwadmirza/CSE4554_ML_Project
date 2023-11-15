    def run(self):
        compile_results = None
        if self.args.compile:
            compile_results = CompileTask.run(self)
            if any(r.error is not None for r in compile_results):
                dbt.ui.printer.print_timestamped_line(
                    'compile failed, cannot generate docs'
                )
                return CatalogResults(
                    {}, datetime.utcnow(), compile_results, None
                )

        shutil.copyfile(
            DOCS_INDEX_FILE_PATH,
            os.path.join(self.config.target_path, 'index.html'))

        if self.manifest is None:
            raise InternalException(
                'self.manifest was None in run!'
            )

        adapter = get_adapter(self.config)
        with adapter.connection_named('generate_catalog'):
            dbt.ui.printer.print_timestamped_line("Building catalog")
            catalog_table, exceptions = adapter.get_catalog(self.manifest)

        catalog_data: List[PrimitiveDict] = [
            dict(zip(catalog_table.column_names, map(_coerce_decimal, row)))
            for row in catalog_table
        ]

        catalog = Catalog(catalog_data)

        errors: Optional[List[str]] = None
        if exceptions:
            errors = [str(e) for e in exceptions]

        results = self.get_catalog_results(
            nodes=catalog.make_unique_id_map(self.manifest),
            generated_at=datetime.utcnow(),
            compile_results=compile_results,
            errors=errors,
        )

        path = os.path.join(self.config.target_path, CATALOG_FILENAME)
        results.write(path)
        write_manifest(self.config, self.manifest)

        if exceptions:
            logger.error(
                'dbt encountered {} failure{} while writing the catalog'
                .format(len(exceptions), (len(exceptions) != 1) * 's')
            )

        dbt.ui.printer.print_timestamped_line(
            'Catalog written to {}'.format(os.path.abspath(path))
        )

        return results