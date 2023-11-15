def get_uniq_name(name: str, excludes: Set[str], camel: bool = False) -> str:
    uniq_name: str = name
    count: int = 1
    while uniq_name in excludes:
        if camel:
            uniq_name = f'{name}{count}'
        else:
            uniq_name = f'{name}_{count}'
        count += 1
    return uniq_name