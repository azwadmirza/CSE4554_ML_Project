    def __init__(self, description, enabled=True, json=False):
        """
        Args:
            description (str):
                The name of the progress bar, shown on left side of output.
            enabled (bool):
                If False, usage is a no-op.
            json (bool):
                If true, outputs json progress to stdout rather than a progress bar.
                Currently, the json format assumes this is only used for "fetch", which
                maintains backward compatibility with conda 4.3 and earlier behavior.
        """
        self.description = description
        self.enabled = enabled
        self.json = json

        if json:
            pass
        elif enabled:
            bar_format = "{desc}{bar} | {percentage:3.0f}% "
            self.pbar = tqdm(desc=description, bar_format=bar_format, ascii=True, total=1)