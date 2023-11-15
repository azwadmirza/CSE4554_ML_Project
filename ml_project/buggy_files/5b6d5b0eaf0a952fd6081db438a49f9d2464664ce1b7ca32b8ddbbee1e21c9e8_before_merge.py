    def format_table_metadata(self, record) -> metadata_model_whale.TableMetadata:
        block_template = textwrap.dedent(
            """            # `{schema}.{name}`{view_statement}
            `{database}`{cluster_statement}
            {description}
            {column_details_delimiter}
            {columns}
            """
        )

        formatted_columns = self.format_columns(record)

        if record.description:
            if type(record.description) == DescriptionMetadata:
                description = record.description._text + "\n"
            else:
                description = str(record.description) + "\n"
        else:
            description = ""

        if record.cluster == "None":  # edge case for Hive Metastore
            cluster = None
        else:
            cluster = record.cluster

        if cluster is not None:
            cluster_statement = f"| `{cluster}`"
        else:
            cluster_statement = ""

        markdown_blob = block_template.format(
            schema=record.schema,
            name=record.name,
            view_statement=" [view]" if record.is_view else "",
            database=record.database,
            cluster_statement=cluster_statement,
            description=description,
            column_details_delimiter=COLUMN_DETAILS_DELIMITER,
            columns=formatted_columns,
        )

        return metadata_model_whale.TableMetadata(
            database=record.database,
            cluster=record.cluster,
            schema=record.schema,
            name=record.name,
            markdown_blob=markdown_blob,
        )