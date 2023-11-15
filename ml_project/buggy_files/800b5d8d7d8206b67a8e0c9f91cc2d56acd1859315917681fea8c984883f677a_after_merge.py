def record_sql(sql, params, cursor=None):
    # type: (Any, Any, Any) -> None
    hub = Hub.current
    if hub.get_integration(DjangoIntegration) is None:
        return

    with capture_internal_exceptions():
        if cursor and hasattr(cursor, "mogrify"):  # psycopg2
            real_sql = cursor.mogrify(sql, params)
            with capture_internal_exceptions():
                if isinstance(real_sql, bytes):
                    real_sql = real_sql.decode(cursor.connection.encoding)
        else:
            real_sql, real_params = format_sql(sql, params)

            if real_params:
                try:
                    real_sql = format_and_strip(real_sql, real_params)
                except Exception:
                    pass
        hub.add_breadcrumb(message=real_sql, category="query")