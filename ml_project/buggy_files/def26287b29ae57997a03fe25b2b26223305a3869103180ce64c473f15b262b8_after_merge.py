    def show_table(self, result):
        table = result.node.agate_table
        rand_table = table.order_by(lambda x: random.random())

        schema = result.node.schema
        alias = result.node.alias

        header = "Random sample of table: {}.{}".format(schema, alias)
        logger.info("")
        logger.info(header)
        logger.info("-" * len(header))
        rand_table.print_table(max_rows=10, max_columns=None)
        logger.info("")