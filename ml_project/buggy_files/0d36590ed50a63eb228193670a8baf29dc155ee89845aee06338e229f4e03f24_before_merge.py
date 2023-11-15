    def _localize_check(self, fn):
        # If the file exists, use it.  If not, set it to None.
        root_dir = os.path.dirname(self.output_dir)
        full_fn = os.path.join(root_dir, fn)
        if os.path.exists(full_fn):
            return full_fn
        return None