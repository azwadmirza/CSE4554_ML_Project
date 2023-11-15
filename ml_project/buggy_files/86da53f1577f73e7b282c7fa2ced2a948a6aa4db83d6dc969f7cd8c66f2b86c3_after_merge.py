    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(GlueExtractor.DEFAULT_CONFIG)
        self._filters = conf.get(GlueExtractor.FILTER_KEY)
        self._connection_name = conf.get(GlueExtractor.CONNECTION_NAME_KEY) or ""
        self._is_location_parsing_enabled = conf.get(
            GlueExtractor.IS_LOCATION_PARSING_ENABLED_KEY
        )
        self._glue = boto3.client("glue")
        self._extract_iter: Union[None, Iterator] = None