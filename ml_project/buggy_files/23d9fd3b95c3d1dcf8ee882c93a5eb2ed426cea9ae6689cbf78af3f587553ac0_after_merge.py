    def _plot_figure(self, idx):
        from .display_hooks import display_figure
        fig = self.plot[idx]
        if OutputMagic.options['backend'] == 'd3':
            import mpld3
            mpld3.plugins.connect(fig, mpld3.plugins.MousePosition(fontsize=14))
            return mpld3.fig_to_dict(fig)
        return display_figure(fig, allow_nbagg=False)