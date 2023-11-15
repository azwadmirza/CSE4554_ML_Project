    def _run_parser(self, class_n, key, name):
        test_name = {"creator": "can_create", "activators": "supports"}
        func_name = test_name.get(key)
        try:
            if func_name is not None:
                prev = getattr(class_n, func_name)

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

                setattr(class_n, func_name, a)
            yield
        finally:
            if func_name is not None:
                # noinspection PyUnboundLocalVariable
                setattr(class_n, func_name, prev)