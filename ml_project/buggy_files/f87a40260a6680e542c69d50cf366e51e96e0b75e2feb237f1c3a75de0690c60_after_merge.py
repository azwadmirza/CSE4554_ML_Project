    def set_group_if_different(self, path, group, changed, diff=None, expand=True):
        b_path = to_bytes(path, errors='surrogate_or_strict')
        if expand:
            b_path = os.path.expanduser(os.path.expandvars(b_path))
        if group is None:
            return changed
        orig_uid, orig_gid = self.user_and_group(b_path, expand)
        try:
            gid = int(group)
        except ValueError:
            try:
                gid = grp.getgrnam(group).gr_gid
            except KeyError:
                path = to_text(b_path)
                self.fail_json(path=path, msg='chgrp failed: failed to look up group %s' % group)

        if orig_gid != gid:
            if diff is not None:
                if 'before' not in diff:
                    diff['before'] = {}
                diff['before']['group'] = orig_gid
                if 'after' not in diff:
                    diff['after'] = {}
                diff['after']['group'] = gid

            if self.check_mode:
                return True
            try:
                os.lchown(b_path, -1, gid)
            except OSError:
                path = to_text(b_path)
                self.fail_json(path=path, msg='chgrp failed')
            changed = True
        return changed