    def status_printer(_, total=None, desc=None, ncols=None):
        """
        Manage the printing of an IPython/Jupyter Notebook progress bar widget.
        """
        # Fallback to text bar if there's no total
        # DEPRECATED: replaced with an 'info' style bar
        # if not total:
        #    return super(tqdm_notebook, tqdm_notebook).status_printer(file)

        # fp = file

        # Prepare IPython progress bar
        try:
            if total:
                pbar = IProgress(min=0, max=total)
            else:  # No total? Show info style bar with no progress tqdm status
                pbar = IProgress(min=0, max=1)
                pbar.value = 1
                pbar.bar_style = 'info'
        except NameError:
            # #187 #451 #558
            raise ImportError(
                "FloatProgress not found. Please update jupyter and ipywidgets."
                " See https://ipywidgets.readthedocs.io/en/stable"
                "/user_install.html")

        if desc:
            pbar.description = desc
            if IPYW >= 7:
                pbar.style.description_width = 'initial'
        # Prepare status text
        ptext = HTML()
        # Only way to place text to the right of the bar is to use a container
        container = HBox(children=[pbar, ptext])
        # Prepare layout
        if ncols is not None:  # use default style of ipywidgets
            # ncols could be 100, "100px", "100%"
            ncols = str(ncols)  # ipywidgets only accepts string
            try:
                if int(ncols) > 0:  # isnumeric and positive
                    ncols += 'px'
            except ValueError:
                pass
            pbar.layout.flex = '2'
            container.layout.width = ncols
            container.layout.display = 'inline-flex'
            container.layout.flex_flow = 'row wrap'
        display(container)

        return container