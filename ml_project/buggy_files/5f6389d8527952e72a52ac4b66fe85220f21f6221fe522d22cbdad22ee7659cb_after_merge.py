def create_index(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("DROP INDEX memory_source_fulltext")
    schema_editor.execute(
        "CREATE INDEX memory_source_trgm ON memory_memory USING GIN (source gin_trgm_ops)"
    )