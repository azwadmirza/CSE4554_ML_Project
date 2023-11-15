def record_sql(sql, params):
    # type: (Any, Any) -> None
    hub = Hub.current
    if hub.get_integration(DjangoIntegration) is None:
        return
    real_sql, real_params = format_sql(sql, params)

    if real_params:
        try:
            real_sql = format_and_strip(real_sql, real_params)
        except Exception:
            pass

    hub.add_breadcrumb(message=real_sql, category="query")