def false_only(t: Type) -> Type:
    """
    Restricted version of t with only False-ish values
    """
    if not t.can_be_false:
        # All values of t are True-ish, so there are no false values in it
        return UninhabitedType(line=t.line)
    elif not t.can_be_true:
        # All values of t are already False-ish, so false_only is idempotent in this case
        return t
    elif isinstance(t, UnionType):
        # The false version of a union type is the union of the false versions of its components
        new_items = [false_only(item) for item in t.items]
        return UnionType.make_simplified_union(new_items, line=t.line, column=t.column)
    else:
        new_t = copy_type(t)
        new_t.can_be_true = False
        return new_t