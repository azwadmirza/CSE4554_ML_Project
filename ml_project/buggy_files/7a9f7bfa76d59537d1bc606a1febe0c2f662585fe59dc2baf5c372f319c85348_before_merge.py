def typespec_to_str(typespec: typing.Any) -> str:
    if typespec in (str, int, bool):
        t = typespec.__name__
    elif typespec == typing.Optional[str]:
        t = 'optional str'
    elif typespec == typing.Sequence[str]:
        t = 'sequence of str'
    else:
        raise NotImplementedError
    return t