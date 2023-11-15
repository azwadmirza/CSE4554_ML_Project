    def _is_role(self, path):
        ''' imperfect role detection, roles are still valid w/o tasks|meta/main.yml|yaml|etc '''

        b_path = to_bytes(path, errors='surrogate_or_strict')
        b_upath = to_bytes(unfrackpath(path, follow=False), errors='surrogate_or_strict')

        for b_finddir in (b'meta', b'tasks'):
            for b_suffix in (b'.yml', b'.yaml', b''):
                b_main = b'main%s' % (b_suffix)
                b_tasked = os.path.join(b_finddir, b_main)

                if (
                    RE_TASKS.search(path) and
                    os.path.exists(os.path.join(b_path, b_main)) or
                    os.path.exists(os.path.join(b_upath, b_tasked)) or
                    os.path.exists(os.path.join(os.path.dirname(b_path), b_tasked))
                ):
                    return True
        return False