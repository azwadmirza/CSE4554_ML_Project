    def cache_key(self, query_obj: QueryObject, **kwargs: Any) -> Optional[str]:
        extra_cache_keys = self.datasource.get_extra_cache_keys(query_obj.to_dict())

        cache_key = (
            query_obj.cache_key(
                datasource=self.datasource.uid,
                extra_cache_keys=extra_cache_keys,
                rls=security_manager.get_rls_ids(self.datasource)
                if config["ENABLE_ROW_LEVEL_SECURITY"]
                else [],
                changed_on=self.datasource.changed_on,
                **kwargs
            )
            if query_obj
            else None
        )
        return cache_key