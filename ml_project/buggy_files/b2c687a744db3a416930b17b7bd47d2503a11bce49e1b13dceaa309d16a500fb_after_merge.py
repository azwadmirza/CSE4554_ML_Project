def tag_macroexpand(tag, tree, compiler):
    """Expand the tag macro "tag" with argument `tree`."""
    load_macros(compiler.module_name)

    tag_macro = _hy_tag[compiler.module_name].get(tag)
    if tag_macro is None:
        try:
            tag_macro = _hy_tag[None][tag]
        except KeyError:
            raise HyTypeError(
                tag,
                "`{0}' is not a defined tag macro.".format(tag)
            )

    expr = tag_macro(tree)
    return replace_hy_obj(expr, tree)