    def set_data(self, data):
        self.closeContext()
        self.data = data
        self.cb_pa.setEnabled(not isinstance(data, SqlTable))
        self.cb_pc.setEnabled(not isinstance(data, SqlTable))
        self.remove_all_rows()
        self.add_button.setDisabled(data is None)
        self.add_all_button.setDisabled(
            data is None or
            len(data.domain.variables) + len(data.domain.metas) > 100)
        if not data:
            self.data_desc = None
            self.commit()
            return
        self.data_desc = report.describe_data_brief(data)
        self.conditions = []
        try:
            self.openContext(data)
        except Exception:
            pass

        variables = list(self._visible_variables(self.data.domain))
        varnames = [v.name if isinstance(v, Variable) else v for v in variables]
        if self.conditions:
            for attr, cond_type, cond_value in self.conditions:
                if attr in varnames:
                    self.add_row(varnames.index(attr), cond_type, cond_value)
                elif attr in self.AllTypes:
                    self.add_row(attr, cond_type, cond_value)
        else:
            self.add_row()

        self.update_info(data, self.data_in_variables, "In: ")
        self.unconditional_commit()