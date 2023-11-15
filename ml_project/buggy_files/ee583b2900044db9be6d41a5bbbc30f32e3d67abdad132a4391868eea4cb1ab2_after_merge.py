def make_overload_method_template(typ, attr, overload_func, inline):
    """
    Make a template class for method *attr* of *typ* overloaded by
    *overload_func*.
    """
    return make_overload_attribute_template(
        typ, attr, overload_func, inline=inline,
        base=_OverloadMethodTemplate,
    )