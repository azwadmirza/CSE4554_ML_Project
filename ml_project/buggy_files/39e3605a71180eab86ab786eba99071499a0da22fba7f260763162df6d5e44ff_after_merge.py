    def save_targets_ensemble(self, targets):
        self._make_internals_directory()
        if not isinstance(targets, np.ndarray):
            raise ValueError('Targets must be of type np.ndarray, but is %s' %
                             type(targets))

        filepath = self._get_targets_ensemble_filename()

        # Try to open the file without locking it, this will reduce the
        # number of times where we erronously keep a lock on the ensemble
        # targets file although the process already was killed
        try:
            existing_targets = np.load(filepath)
            if existing_targets.shape[0] > targets.shape[0] or \
                    (existing_targets.shape == targets.shape and
                         np.allclose(existing_targets, targets)):

                return filepath
        except Exception:
            pass

        lock_path = filepath + '.lock'
        with lockfile.LockFile(lock_path):
            if os.path.exists(filepath):
                existing_targets = np.load(filepath)
                if existing_targets.shape[0] > targets.shape[0] or \
                        (existing_targets.shape == targets.shape and
                         np.allclose(existing_targets, targets)):
                    return filepath

            with tempfile.NamedTemporaryFile('wb', dir=os.path.dirname(
                    filepath), delete=False) as fh:
                np.save(fh, targets.astype(np.float32))
                tempname = fh.name

            os.rename(tempname, filepath)

        return filepath