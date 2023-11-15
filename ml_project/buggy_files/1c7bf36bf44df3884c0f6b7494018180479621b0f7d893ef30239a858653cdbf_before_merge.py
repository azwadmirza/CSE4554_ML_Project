    def set_mode_if_different(self, path, mode, changed, diff=None, expand=True):
        b_path = to_bytes(path, errors='surrogate_then_strict')
        if expand:
            b_path = os.path.expanduser(os.path.expandvars(b_path))
        path = to_text(b_path, errors='surrogate_then_strict')
        path_stat = os.lstat(b_path)

        if mode is None:
            return changed

        if not isinstance(mode, int):
            try:
                mode = int(mode, 8)
            except Exception:
                try:
                    mode = self._symbolic_mode_to_octal(path_stat, mode)
                except Exception:
                    e = get_exception()
                    self.fail_json(path=path,
                                   msg="mode must be in octal or symbolic form",
                                   details=str(e))

                if mode != stat.S_IMODE(mode):
                    # prevent mode from having extra info orbeing invalid long number
                    self.fail_json(path=path, msg="Invalid mode supplied, only permission info is allowed", details=mode)

        prev_mode = stat.S_IMODE(path_stat.st_mode)

        if prev_mode != mode:

            if diff is not None:
                if 'before' not in diff:
                    diff['before'] = {}
                diff['before']['mode'] = '0%03o' % prev_mode
                if 'after' not in diff:
                    diff['after'] = {}
                diff['after']['mode'] = '0%03o' % mode

            if self.check_mode:
                return True
            # FIXME: comparison against string above will cause this to be executed
            # every time
            try:
                if hasattr(os, 'lchmod'):
                    os.lchmod(b_path, mode)
                else:
                    if not os.path.islink(b_path):
                        os.chmod(b_path, mode)
                    else:
                        # Attempt to set the perms of the symlink but be
                        # careful not to change the perms of the underlying
                        # file while trying
                        underlying_stat = os.stat(b_path)
                        os.chmod(b_path, mode)
                        new_underlying_stat = os.stat(b_path)
                        if underlying_stat.st_mode != new_underlying_stat.st_mode:
                            os.chmod(b_path, stat.S_IMODE(underlying_stat.st_mode))
            except OSError:
                e = get_exception()
                if os.path.islink(b_path) and e.errno == errno.EPERM:  # Can't set mode on symbolic links
                    pass
                elif e.errno in (errno.ENOENT, errno.ELOOP): # Can't set mode on broken symbolic links
                    pass
                else:
                    raise e
            except Exception:
                e = get_exception()
                self.fail_json(path=path, msg='chmod failed', details=str(e))

            path_stat = os.lstat(b_path)
            new_mode = stat.S_IMODE(path_stat.st_mode)

            if new_mode != prev_mode:
                changed = True
        return changed