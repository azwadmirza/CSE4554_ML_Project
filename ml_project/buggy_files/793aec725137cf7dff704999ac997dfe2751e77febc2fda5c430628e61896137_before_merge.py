    def display(self, workspace, figure):
        if not self.show_window:
            return

        figure.set_subplots((2, 2))

        renumbered_parent_labels = cellprofiler.gui.tools.renumber_labels_for_display(
                workspace.display_data.parent_labels
        )

        child_labels = workspace.display_data.child_labels

        parents_of = workspace.display_data.parents_of

        #
        # discover the mapping so that we can apply it to the children
        #
        mapping = numpy.arange(workspace.display_data.parent_count + 1)

        mapping[workspace.display_data.parent_labels.flatten()] = renumbered_parent_labels.flatten()

        parent_labeled_children = numpy.zeros(child_labels.shape, int)

        mask = child_labels > 0

        parent_labeled_children[mask] = mapping[parents_of[child_labels[mask] - 1]]

        figure.subplot_imshow_labels(
            0,
            0,
            renumbered_parent_labels,
            title=self.parent_name.value,
            renumber=False
        )

        figure.subplot_imshow_labels(
            1,
            0,
            child_labels,
            title=self.sub_object_name.value,
            sharex=figure.subplot(0, 0),
            sharey=figure.subplot(0, 0)
        )

        figure.subplot_imshow_labels(
            0,
            1,
            parent_labeled_children,
            "{} labeled by {}".format(self.sub_object_name.value, self.parent_name.value),
            renumber=False,
            sharex=figure.subplot(0, 0),
            sharey=figure.subplot(0, 0)
        )