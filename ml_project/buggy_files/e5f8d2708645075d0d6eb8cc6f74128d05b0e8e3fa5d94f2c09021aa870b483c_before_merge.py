def setup(app: "Sphinx") -> Dict[str, Any]:
    app.connect('config-inited', merge_source_suffix)

    return {
        'version': 'builtin',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }