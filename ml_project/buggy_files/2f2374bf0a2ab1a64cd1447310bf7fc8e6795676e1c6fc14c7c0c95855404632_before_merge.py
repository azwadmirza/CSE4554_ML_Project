    def run(self, workspace):
        if self.show_window:
            m = workspace.get_measurements()
            # Get plates
            plates = m.get_all_measurements(cpmeas.IMAGE, self.plate_name.value)
            # Get wells
            if self.well_format == WF_NAME:
                wells = m.get_all_measurements(cpmeas.IMAGE, self.well_name.value)
            elif self.well_format == WF_ROWCOL:
                wells = ['%s%s'%(x,y) for x,y in zip(m.get_all_measurements(cpmeas.IMAGE, self.well_row.value),
                                                     m.get_all_measurements(cpmeas.IMAGE, self.well_col.value))]
            # Get data to plot
            data = m.get_all_measurements(self.get_object(), self.plot_measurement.value)

            # Construct a dict mapping plates and wells to lists of measurements
            pm_dict = {}
            for plate, well, data in zip(plates, wells, data):
                if data is None:
                    continue
                if plate in pm_dict:
                    if well in pm_dict[plate]:
                        pm_dict[plate][well] += [data]
                    else:
                        pm_dict[plate].update({well : [data]})
                else:
                    pm_dict[plate] = {well : [data]}

            for plate, sub_dict in pm_dict.items():            
                for well, vals in sub_dict.items():
                    vals = np.hstack(vals)
                    if self.agg_method == AGG_AVG:
                        pm_dict[plate][well] = np.mean(vals)
                    elif self.agg_method == AGG_STDEV:
                        pm_dict[plate][well] = np.std(vals)
                    elif self.agg_method == AGG_MEDIAN:
                        pm_dict[plate][well] = np.median(vals)
                    elif self.agg_method == AGG_CV:
                        pm_dict[plate][well] = np.std(vals) / np.mean(vals)
                    else:
                        raise NotImplemented
            workspace.display_data.pm_dict = pm_dict