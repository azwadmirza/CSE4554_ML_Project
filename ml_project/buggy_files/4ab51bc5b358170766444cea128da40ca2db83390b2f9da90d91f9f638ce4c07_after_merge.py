    def __init__(self, *args, **kwargs):
        # Setup default output
        if kwargs.get('file', sys.stderr) is sys.stderr:
            kwargs['file'] = sys.stdout  # avoid the red block in IPython

        # Initialize parent class + avoid printing by using gui=True
        kwargs['gui'] = True
        kwargs.setdefault('bar_format', '{l_bar}{bar}{r_bar}')
        kwargs['bar_format'] = kwargs['bar_format'].replace('{bar}', '<bar/>')
        super(tqdm_notebook, self).__init__(*args, **kwargs)
        if self.disable or not kwargs['gui']:
            return

        # Get bar width
        self.ncols = '100%' if self.dynamic_ncols else kwargs.get("ncols", None)

        # Replace with IPython progress bar display (with correct total)
        unit_scale = 1 if self.unit_scale is True else self.unit_scale or 1
        total = self.total * unit_scale if self.total else self.total
        self.container = self.status_printer(
            self.fp, total, self.desc, self.ncols)
        self.sp = self.display

        # Print initial bar state
        if not self.disable:
            self.display()