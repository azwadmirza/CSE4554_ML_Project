    def user_and_group(self, path, expand=True):
        b_path = to_bytes(path, errors='surrogate_then_strict')
        if expand:
            b_path = os.path.expanduser(os.path.expandvars(b_path))
        st = os.lstat(b_path)
        uid = st.st_uid
        gid = st.st_gid
        return (uid, gid)