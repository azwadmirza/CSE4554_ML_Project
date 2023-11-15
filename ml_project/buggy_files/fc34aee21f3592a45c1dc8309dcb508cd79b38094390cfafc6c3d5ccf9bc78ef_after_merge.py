def get__all__entries(obj):
    """returns the strings in the __all__ attribute"""
    try:
        words = getattr(obj, '__all__')
    except:
        return []
    
    return [cast_unicode_py2(w) for w in words if isinstance(w, string_types)]