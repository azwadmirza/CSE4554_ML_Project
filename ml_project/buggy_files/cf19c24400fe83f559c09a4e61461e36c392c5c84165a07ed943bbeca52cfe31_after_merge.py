def major_versions_differ(v1: str, v2: str) -> bool:
    return v1.split('.')[0:2] != v2.split('.')[0:2]