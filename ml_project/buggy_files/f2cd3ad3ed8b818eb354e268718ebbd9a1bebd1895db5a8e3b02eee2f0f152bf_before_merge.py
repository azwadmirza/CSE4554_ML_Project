    def __enter__(self):
        enabled = os.environ.get('CONDA_INSTRUMENTATION_ENABLED')
        if enabled and boolify(enabled):
            self.start_time = time()