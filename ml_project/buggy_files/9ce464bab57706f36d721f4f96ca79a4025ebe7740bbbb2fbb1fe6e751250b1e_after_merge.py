def get_uniq_name(name: str, excludes: Set[str]) -> str:
    uniq_name: str = name
    count: int = 1
    while uniq_name in excludes:
        uniq_name = f'{name}_{count}'
        count += 1
    return uniq_name