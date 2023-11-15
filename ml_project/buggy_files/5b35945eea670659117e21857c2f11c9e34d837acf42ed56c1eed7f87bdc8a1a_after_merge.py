def execute_sql_statement(sql_statement, query, user_name, session, cursor):
    """Executes a single SQL statement"""
    query_id = query.id
    database = query.database
    db_engine_spec = database.db_engine_spec
    parsed_query = ParsedQuery(sql_statement)
    sql = parsed_query.stripped()
    SQL_MAX_ROWS = app.config["SQL_MAX_ROW"]

    if not parsed_query.is_readonly() and not database.allow_dml:
        raise SqlLabSecurityException(
            _("Only `SELECT` statements are allowed against this database")
        )
    if query.select_as_cta:
        if not parsed_query.is_select():
            raise SqlLabException(
                _(
                    "Only `SELECT` statements can be used with the CREATE TABLE "
                    "feature."
                )
            )
        if not query.tmp_table_name:
            start_dttm = datetime.fromtimestamp(query.start_time)
            query.tmp_table_name = "tmp_{}_table_{}".format(
                query.user_id, start_dttm.strftime("%Y_%m_%d_%H_%M_%S")
            )
        sql = parsed_query.as_create_table(query.tmp_table_name)
        query.select_as_cta_used = True
    if parsed_query.is_select():
        if SQL_MAX_ROWS and (not query.limit or query.limit > SQL_MAX_ROWS):
            query.limit = SQL_MAX_ROWS
        if query.limit:
            sql = database.apply_limit_to_sql(sql, query.limit)

    # Hook to allow environment-specific mutation (usually comments) to the SQL
    SQL_QUERY_MUTATOR = config["SQL_QUERY_MUTATOR"]
    if SQL_QUERY_MUTATOR:
        sql = SQL_QUERY_MUTATOR(sql, user_name, security_manager, database)

    try:
        if log_query:
            log_query(
                query.database.sqlalchemy_uri,
                query.executed_sql,
                query.schema,
                user_name,
                __name__,
                security_manager,
            )
        query.executed_sql = sql
        session.commit()
        with stats_timing("sqllab.query.time_executing_query", stats_logger):
            logger.info(f"Query {query_id}: Running query: \n{sql}")
            db_engine_spec.execute(cursor, sql, async_=True)
            logger.info(f"Query {query_id}: Handling cursor")
            db_engine_spec.handle_cursor(cursor, query, session)

        with stats_timing("sqllab.query.time_fetching_results", stats_logger):
            logger.debug(
                "Query {}: Fetching data for query object: {}".format(
                    query_id, query.to_dict()
                )
            )
            data = db_engine_spec.fetch_data(cursor, query.limit)

    except SoftTimeLimitExceeded as e:
        logger.exception(f"Query {query_id}: {e}")
        raise SqlLabTimeoutException(
            "SQL Lab timeout. This environment's policy is to kill queries "
            "after {} seconds.".format(SQLLAB_TIMEOUT)
        )
    except Exception as e:
        logger.exception(f"Query {query_id}: {e}")
        raise SqlLabException(db_engine_spec.extract_error_message(e))

    logger.debug(f"Query {query_id}: Fetching cursor description")
    cursor_description = cursor.description
    return SupersetDataFrame(data, cursor_description, db_engine_spec)