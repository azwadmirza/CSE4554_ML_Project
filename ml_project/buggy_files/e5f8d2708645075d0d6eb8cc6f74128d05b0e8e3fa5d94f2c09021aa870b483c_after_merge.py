def setup(app: "Sphinx") -> Dict[str, Any]:
    app.connect('config-inited', merge_source_suffix, priority=800)

    return {
        'version': 'builtin',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }