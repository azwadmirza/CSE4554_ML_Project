    def set(self, **kwargs):
        """Set attributes on each subplot Axes."""
        for ax in self.axes.flat:
            if ax is not None:  # Handle removed axes
                ax.set(**kwargs)
        return self