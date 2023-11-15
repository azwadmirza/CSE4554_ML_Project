def get_annotation_compexity(annotation_node: _Annotation) -> int:
    """
    Recursevly counts complexity of annotation nodes.

    When annotations are written as strings,
    we additionally parse them to ``ast`` nodes.
    """
    if isinstance(annotation_node, ast.Str):
        # try to parse string-wrapped annotations
        try:
            annotation_node = ast.parse(  # type: ignore
                annotation_node.s,
            ).body[0].value
        except (SyntaxError, IndexError):
            return 1

    if isinstance(annotation_node, ast.Subscript):
        return 1 + get_annotation_compexity(
            annotation_node.slice.value,  # type: ignore
        )
    elif isinstance(annotation_node, (ast.Tuple, ast.List)):
        return max(
            (get_annotation_compexity(node) for node in annotation_node.elts),
            default=1,
        )
    return 1