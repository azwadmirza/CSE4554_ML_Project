def get_jinja_env():
    from datetime import datetime
    from ..utils import readable_size

    _jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    )

    def format_ts(value):
        if value is None:
            return None
        return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')

    _jinja_env.filters['format_ts'] = format_ts
    _jinja_env.filters['readable_size'] = readable_size
    return _jinja_env