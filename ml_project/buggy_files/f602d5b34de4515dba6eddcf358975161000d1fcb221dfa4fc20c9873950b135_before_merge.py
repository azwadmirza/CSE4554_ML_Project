def setup(app: "Sphinx") -> Dict[str, Any]:
    app.connect('config-inited', verify_needs_extensions)

    return {
        'version': 'builtin',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }