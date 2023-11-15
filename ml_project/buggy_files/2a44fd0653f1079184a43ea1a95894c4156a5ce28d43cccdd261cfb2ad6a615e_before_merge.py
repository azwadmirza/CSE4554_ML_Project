def configure_glue_extractors(connection: ConnectionConfigSchema):
    Extractor = GlueExtractor
    extractor = Extractor()
    scope = extractor.get_scope()

    conf = ConfigFactory.from_dict(
        {
            f"{scope}.{Extractor.CONNECTION_NAME_KEY}": connection.name,
            f"{scope}.{Extractor.FILTER_KEY}": connection.filter_key,
        }
    )

    extractors = [extractor]
    return extractors, conf