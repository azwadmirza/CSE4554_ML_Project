def _make_attr_tuple_class(cls_name, attr_names):
    """
    Create a tuple subclass to hold `Attribute`s for an `attrs` class.

    The subclass is a bare tuple with properties for names.

    class MyClassAttributes(tuple):
        __slots__ = ()
        x = property(itemgetter(0))
    """
    attr_class_name = "{}Attributes".format(cls_name)
    attr_class_template = [
        "class {}(tuple):".format(attr_class_name),
        "    __slots__ = ()",
    ]
    if attr_names:
        for i, attr_name in enumerate(attr_names):
            attr_class_template.append(
                _tuple_property_pat.format(index=i, attr_name=attr_name)
            )
    else:
        attr_class_template.append("    pass")
    globs = {"_attrs_itemgetter": itemgetter, "_attrs_property": property}
    eval(compile("\n".join(attr_class_template), "", "exec"), globs)

    return globs[attr_class_name]