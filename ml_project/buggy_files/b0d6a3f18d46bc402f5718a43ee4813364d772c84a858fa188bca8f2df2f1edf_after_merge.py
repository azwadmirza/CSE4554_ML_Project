    def read_sql(cls, sql, con, index_col=None, **kwargs):
        """Reads a SQL query or database table into a DataFrame.
        Args:
            sql: string or SQLAlchemy Selectable (select or text object) SQL query to be
                executed or a table name.
            con: SQLAlchemy connectable (engine/connection) or database string URI or
                DBAPI2 connection (fallback mode)
            index_col: Column(s) to set as index(MultiIndex).
            kwargs: Pass into pandas.read_sql function.
        """
        if cls.read_sql_remote_task is None:
            return super(RayIO, cls).read_sql(sql, con, index_col=index_col, **kwargs)

        import sqlalchemy as sa

        # In the case that we are given a SQLAlchemy Connection or Engine, the objects
        # are not pickleable. We have to convert it to the URL string and connect from
        # each of the workers.
        if isinstance(con, (sa.engine.Engine, sa.engine.Connection)):
            con = repr(con.engine.url)
        row_cnt_query = "SELECT COUNT(*) FROM ({}) as foo".format(sql)
        row_cnt = pandas.read_sql(row_cnt_query, con).squeeze()
        cols_names_df = pandas.read_sql(
            "SELECT * FROM ({}) as foo LIMIT 0".format(sql), con, index_col=index_col
        )
        cols_names = cols_names_df.columns
        num_parts = cls.frame_mgr_cls._compute_num_partitions()
        partition_ids = []
        index_ids = []
        limit = math.ceil(row_cnt / num_parts)
        for part in range(num_parts):
            offset = part * limit
            query = "SELECT * FROM ({}) as foo LIMIT {} OFFSET {}".format(
                sql, limit, offset
            )
            partition_id = cls.read_sql_remote_task._remote(
                args=(num_parts, query, con, index_col, kwargs),
                num_return_vals=num_parts + 1,
            )
            partition_ids.append(
                [cls.frame_partition_cls(obj) for obj in partition_id[:-1]]
            )
            index_ids.append(partition_id[-1])

        if index_col is None:  # sum all lens returned from partitions
            index_lens = ray.get(index_ids)
            new_index = pandas.RangeIndex(sum(index_lens))
        else:  # concat index returned from partitions
            index_lst = [x for part_index in ray.get(index_ids) for x in part_index]
            new_index = pandas.Index(index_lst).set_names(index_col)

        new_query_compiler = cls.query_compiler_cls(
            cls.frame_mgr_cls(np.array(partition_ids)), new_index, cols_names
        )
        return new_query_compiler