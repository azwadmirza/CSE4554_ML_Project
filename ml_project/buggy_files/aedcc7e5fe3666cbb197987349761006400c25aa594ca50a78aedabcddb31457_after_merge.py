                def a(*args, **kwargs):
                    prev(*args, **kwargs)
                    if key == "activators":
                        return True
                    elif key == "creator":
                        if name == "venv":
                            from virtualenv.create.via_global_ref.venv import ViaGlobalRefMeta

                            meta = ViaGlobalRefMeta()
                            meta.symlink_error = None
                            return meta
                        from virtualenv.create.via_global_ref.builtin.via_global_self_do import BuiltinViaGlobalRefMeta

                        meta = BuiltinViaGlobalRefMeta()
                        meta.symlink_error = None
                        return meta
                    raise RuntimeError