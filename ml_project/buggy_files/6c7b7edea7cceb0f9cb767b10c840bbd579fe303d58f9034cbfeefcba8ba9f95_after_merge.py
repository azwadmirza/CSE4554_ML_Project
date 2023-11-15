def env_before_read_docs(app, env, docnames):
    docnames.sort(key=lambda x: 0 if "examples" in x else 1)
    for name in [x for x in docnames if env.doc2path(x).endswith(".py")]:
        if not name.startswith(tuple(env.app.config.bokeh_plot_pyfile_include_dirs)):
            env.found_docs.remove(name)
            docnames.remove(name)