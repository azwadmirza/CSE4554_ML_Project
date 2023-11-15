    def crawl_legend(self, ax, legend):
        """
        Recursively look through objects in legend children
        """
        legendElements = list(utils.iter_all_children(legend._legend_box,
                                                      skipContainers=True))
        legendElements.append(legend.legendPatch)
        for child in legendElements:
            # force a large zorder so it appears on top
            child.set_zorder(1E6 + child.get_zorder())

            try:
                # What kind of object...
                if isinstance(child, matplotlib.patches.Patch):
                    self.draw_patch(ax, child, force_trans=ax.transAxes)
                elif isinstance(child, matplotlib.text.Text):
                    if not (child is legend.get_children()[-1]
                            and child.get_text() == 'None'):
                        self.draw_text(ax, child, force_trans=ax.transAxes)
                elif isinstance(child, matplotlib.lines.Line2D):
                    self.draw_line(ax, child, force_trans=ax.transAxes)
                elif isinstance(child, matplotlib.collections.Collection):
                    self.draw_collection(ax, child,
                                         force_pathtrans=ax.transAxes)
                else:
                    warnings.warn("Legend element %s not impemented" % child)
            except NotImplementedError:
                warnings.warn("Legend element %s not impemented" % child)