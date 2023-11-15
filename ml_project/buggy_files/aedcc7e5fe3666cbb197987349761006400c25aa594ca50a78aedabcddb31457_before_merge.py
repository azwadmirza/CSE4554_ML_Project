                def a(*args, **kwargs):
                    prev(*args, **kwargs)
                    if key == "activators":
                        return True
                    elif key == "creator":
                        if name == "venv":
                            from virtualenv.create.via_global_ref.venv import Meta

                            return Meta(True, True)
                        from virtualenv.create.via_global_ref.builtin.via_global_self_do import Meta

                        return Meta([], True, True)
                    raise RuntimeError