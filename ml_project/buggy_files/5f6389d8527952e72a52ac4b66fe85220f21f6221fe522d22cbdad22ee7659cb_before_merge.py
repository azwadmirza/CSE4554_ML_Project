def create_index(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    # This ensures that extensions are loaded into the session. Without that
    # the next ALTER database fails unless we're running as superuser (which
    # is allowed to set non existing parameters, so missing extension doesn't
    # matter)
    # See https://www.postgresql.org/message-id/6376.1533675236%40sss.pgh.pa.us
    schema_editor.execute("SELECT show_limit()")

    schema_editor.execute(
        "ALTER DATABASE {} SET pg_trgm.similarity_threshold = 0.7".format(
            schema_editor.connection.settings_dict["NAME"]
        )
    )
    schema_editor.execute("DROP INDEX memory_source_fulltext")
    schema_editor.execute(
        "CREATE INDEX memory_source_trgm ON memory_memory USING GIN (source gin_trgm_ops)"
    )