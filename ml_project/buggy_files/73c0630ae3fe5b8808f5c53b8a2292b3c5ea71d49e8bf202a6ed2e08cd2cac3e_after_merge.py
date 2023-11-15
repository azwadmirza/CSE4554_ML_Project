def generate_bql_grammar_json():
    """Generate a JSON file with BQL grammar attributes.

    The online code editor needs to have the list of available columns,
    functions, and keywords for syntax highlighting and completion.

    Should be run whenever the BQL changes."""

    target_env = query_env.TargetsEnvironment()
    data = {
        "columns": sorted(set(_env_to_list(target_env.columns))),
        "functions": sorted(set(_env_to_list(target_env.functions))),
        "keywords": sorted({kw.lower() for kw in query_parser.Lexer.keywords}),
    }
    path = os.path.join(
        os.path.dirname(__file__),
        "../fava/static/javascript/codemirror/bql-grammar.json",
    )
    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file)