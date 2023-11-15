    def _repr_html_(self):
        """A pretty representation for Jupyter notebooks that includes header
        details and information about all scalar arrays"""
        fmt = ""
        if self.n_arrays > 0:
            fmt += "<table>"
            fmt += "<tr><th>Header</th><th>Data Arrays</th></tr>"
            fmt += "<tr><td>"
        # Get the header info
        fmt += self.head(display=False, html=True)
        # Fill out scalar arrays
        if self.n_arrays > 0:
            fmt += "</td><td>"
            fmt += "\n"
            fmt += "<table>\n"
            titles = ["Name", "Field", "Type", "N Comp", "Min", "Max"]
            fmt += "<tr>" + "".join(["<th>{}</th>".format(t) for t in titles]) + "</tr>\n"
            row = "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>\n"
            row = "<tr>" + "".join(["<td>{}</td>" for i in range(len(titles))]) + "</tr>\n"

            def format_array(key, field):
                """internal helper to foramt array information for printing"""
                arr = get_scalar(self, key, preference=field)
                dl, dh = self.get_data_range(key)
                dl = pyvista.FLOAT_FORMAT.format(dl)
                dh = pyvista.FLOAT_FORMAT.format(dh)
                if key == self.active_scalar_info[1]:
                    key = '<b>{}</b>'.format(key)
                if arr.ndim > 1:
                    ncomp = arr.shape[1]
                else:
                    ncomp = 1
                return row.format(key, field, arr.dtype, ncomp, dl, dh)

            for i in range(self.GetPointData().GetNumberOfArrays()):
                key = self.GetPointData().GetArrayName(i)
                fmt += format_array(key, field='Points')
            for i in range(self.GetCellData().GetNumberOfArrays()):
                key = self.GetCellData().GetArrayName(i)
                fmt += format_array(key, field='Cells')
            for i in range(self.GetFieldData().GetNumberOfArrays()):
                key = self.GetFieldData().GetArrayName(i)
                fmt += format_array(key, field='Fields')

            fmt += "</table>\n"
            fmt += "\n"
            fmt += "</td></tr> </table>"
        return fmt