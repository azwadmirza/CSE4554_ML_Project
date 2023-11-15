def check_libraries():
    """Check if all needed Python libraries are installed."""
    modules = {
        'jinja2': _missing_str("jinja2"),
        'yaml': _missing_str("PyYAML"),
        'dataclasses': _missing_str("dataclasses"),
        'PyQt5.QtQml': _missing_str("PyQt5.QtQml"),
        'PyQt5.QtSql': _missing_str("PyQt5.QtSql"),
        'PyQt5.QtOpenGL': _missing_str("PyQt5.QtOpenGL"),
    }
    try:
        import importlib.resources
    except ImportError:
        # Backport required
        modules['importlib_resources'] = _missing_str("importlib_resources")
    _check_modules(modules)