def get_query_backoff_handler(details):
    query_id = details["kwargs"]["query_id"]
    logger.error(f"Query with id `{query_id}` could not be retrieved")
    stats_logger.incr("error_attempting_orm_query_{}".format(details["tries"] - 1))
    logger.error(f"Query {query_id}: Sleeping for a sec before retrying...")