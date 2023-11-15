def debug_print(*args, **kwargs):
    if _DEBUG:
        print(*args, **kwargs)