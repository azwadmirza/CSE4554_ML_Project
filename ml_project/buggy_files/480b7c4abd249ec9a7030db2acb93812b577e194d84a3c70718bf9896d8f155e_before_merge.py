                def wrapper(*args, **kwargs):
                    t.update()
                    return func(*args, **kwargs)