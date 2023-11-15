def escape_xpath_value(value):
    if '"' in value and "'" in value:
        parts_wo_apos = value.split("'")
        escaped = "', \"'\", '".join(parts_wo_apos)
        return f"concat('{escaped}')"
    if "'" in value:
        return f'"{value}"'
    return f"'{value}'"