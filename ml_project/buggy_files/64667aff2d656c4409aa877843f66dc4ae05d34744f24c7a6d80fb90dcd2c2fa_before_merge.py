def get_url(chart):
    """Return external URL for warming up a given chart/table cache."""
    with app.test_request_context():
        baseurl = "{SUPERSET_WEBSERVER_ADDRESS}:{SUPERSET_WEBSERVER_PORT}".format(
            **app.config
        )
        return f"{baseurl}{chart.url}"