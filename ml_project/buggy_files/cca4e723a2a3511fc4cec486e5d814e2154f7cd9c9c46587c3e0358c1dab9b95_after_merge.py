    def cache_key(self, query_obj, **extra):
        """
        The cache key is made out of the key/values in `query_obj`, plus any
        other key/values in `extra`.

        We remove datetime bounds that are hard values, and replace them with
        the use-provided inputs to bounds, which may be time-relative (as in
        "5 days ago" or "now").

        The `extra` arguments are currently used by time shift queries, since
        different time shifts wil differ only in the `from_dttm` and `to_dttm`
        values which are stripped.
        """
        cache_dict = copy.copy(query_obj)
        cache_dict.update(extra)

        for k in ["from_dttm", "to_dttm"]:
            del cache_dict[k]

        cache_dict["time_range"] = self.form_data.get("time_range")
        cache_dict["datasource"] = self.datasource.uid
        cache_dict["extra_cache_keys"] = self.datasource.get_extra_cache_keys(query_obj)
        if config["ENABLE_ROW_LEVEL_SECURITY"]:
            cache_dict["rls"] = security_manager.get_rls_ids(self.datasource)
        cache_dict["changed_on"] = self.datasource.changed_on
        json_data = self.json_dumps(cache_dict, sort_keys=True)
        return hashlib.md5(json_data.encode("utf-8")).hexdigest()