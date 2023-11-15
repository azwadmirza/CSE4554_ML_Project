def get_column_def(columns, column: str, default: str) -> str:
    return default if not has_column(columns, column) else column