def persist_graph(graph, output_file):
    """Plots the graph and persists it into a html file."""
    import networkx as nx

    expg = nx.nx_pydot.to_pydot(graph)

    with open(visualization_html_path(), "r") as file:
        template = file.read()

    # customize content of template by replacing tags
    template = template.replace("// { is-client }", "isClient = true", 1)
    template = template.replace(
        "// { graph-content }", "graph = `{}`".format(expg.to_string()), 1
    )

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(template)