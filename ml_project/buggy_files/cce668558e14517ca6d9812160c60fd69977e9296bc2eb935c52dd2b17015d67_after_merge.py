        def annotate_frame(i):
            axes.set_title("{s.name}".format(s=self[i]))
            axes.set_xlabel(axis_labels_from_ctype(self[i].coordinate_system[0],
                                                   self[i].spatial_units[0]))
            axes.set_ylabel(axis_labels_from_ctype(self[i].coordinate_system[1],
                                                   self[i].spatial_units[1]))