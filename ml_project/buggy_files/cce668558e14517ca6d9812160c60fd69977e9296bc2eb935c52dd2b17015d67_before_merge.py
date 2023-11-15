        def annotate_frame(i):
            axes.set_title("{s.name}".format(s=self[i]))

            # x-axis label
            if self[0].coordinate_system.x == 'HG':
                xlabel = 'Longitude [{lon}'.format(lon=self[i].spatial_units.x)
            else:
                xlabel = 'X-position [{xpos}]'.format(xpos=self[i].spatial_units.x)

            # y-axis label
            if self[0].coordinate_system.y == 'HG':
                ylabel = 'Latitude [{lat}]'.format(lat=self[i].spatial_units.y)
            else:
                ylabel = 'Y-position [{ypos}]'.format(ypos=self[i].spatial_units.y)

            axes.set_xlabel(xlabel)
            axes.set_ylabel(ylabel)