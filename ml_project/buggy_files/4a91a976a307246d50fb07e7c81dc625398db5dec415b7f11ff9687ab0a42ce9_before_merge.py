def compare_helper(this, other, accepted):
    if not isinstance(this, types.ListType):
        return
    if not isinstance(other, types.ListType):
        raise TypingError("list can only be compared to list")

    def impl(this, other):
        return compare(this, other) in accepted
    return impl