    def get_catalog(cls, profile, project_cfg, manifest):
        try:
            table = cls.run_operation(profile, project_cfg, manifest,
                                      GET_CATALOG_OPERATION_NAME)
        finally:
            cls.release_connection(profile, GET_CATALOG_OPERATION_NAME)

        schemas = list({
            node.schema.lower()
            for node in manifest.nodes.values()
        })

        results = table.where(lambda r: r['table_schema'].lower() in schemas)
        return results