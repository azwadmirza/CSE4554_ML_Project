    def get_catalog(cls, profile, project_cfg, manifest):
        try:
            table = cls.run_operation(profile, project_cfg, manifest,
                                      GET_CATALOG_OPERATION_NAME)
        finally:
            cls.release_connection(profile, GET_CATALOG_OPERATION_NAME)

        results = table.where(_filter_schemas(manifest))
        return results