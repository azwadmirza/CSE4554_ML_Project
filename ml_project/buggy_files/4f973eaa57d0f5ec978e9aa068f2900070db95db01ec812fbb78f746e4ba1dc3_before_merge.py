    def set_owner_if_different(self, path, owner, changed, diff=None, expand=True):
        b_path = to_bytes(path, errors='surrogate_then_strict')
        if expand:
            b_path = os.path.expanduser(os.path.expandvars(b_path))
        path = to_text(b_path, errors='surrogate_then_strict')
        if owner is None:
            return changed
        orig_uid, orig_gid = self.user_and_group(path, expand)
        try:
            uid = int(owner)
        except ValueError:
            try:
                uid = pwd.getpwnam(owner).pw_uid
            except KeyError:
                self.fail_json(path=path, msg='chown failed: failed to look up user %s' % owner)
        if orig_uid != uid:

            if diff is not None:
                if 'before' not in diff:
                    diff['before'] = {}
                diff['before']['owner'] = orig_uid
                if 'after' not in diff:
                    diff['after'] = {}
                diff['after']['owner'] = uid

            if self.check_mode:
                return True
            try:
                os.lchown(b_path, uid, -1)
            except OSError:
                self.fail_json(path=path, msg='chown failed')
            changed = True
        return changed