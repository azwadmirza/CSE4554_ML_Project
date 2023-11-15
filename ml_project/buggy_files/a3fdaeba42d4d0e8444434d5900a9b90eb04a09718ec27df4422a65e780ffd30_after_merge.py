    def set_owner_if_different(self, path, owner, changed, diff=None, expand=True):
        b_path = to_bytes(path, errors='surrogate_or_strict')
        if expand:
            b_path = os.path.expanduser(os.path.expandvars(b_path))
        if owner is None:
            return changed
        orig_uid, orig_gid = self.user_and_group(b_path, expand)
        try:
            uid = int(owner)
        except ValueError:
            try:
                uid = pwd.getpwnam(owner).pw_uid
            except KeyError:
                path = to_text(b_path)
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
                path = to_text(b_path)
                self.fail_json(path=path, msg='chown failed')
            changed = True
        return changed