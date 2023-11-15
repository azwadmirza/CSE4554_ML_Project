def get_sql_results(
    ctask,
    query_id,
    rendered_query,
    return_results=True,
    store_results=False,
    user_name=None,
    start_time=None,
    expand_data=False,
):
    """Executes the sql query returns the results."""
    with session_scope(not ctask.request.called_directly) as session:

        try:
            return execute_sql_statements(
                ctask,
                query_id,
                rendered_query,
                return_results,
                store_results,
                user_name,
                session=session,
                start_time=start_time,
                expand_data=expand_data,
            )
        except Exception as e:
            logging.exception(f"Query {query_id}: {e}")
            stats_logger.incr("error_sqllab_unhandled")
            query = get_query(query_id, session)
            return handle_query_error(str(e), query, session)