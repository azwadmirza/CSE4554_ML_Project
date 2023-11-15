    def remove_row(self, rows, grid_sizer, remove_button):
        for i, vw_row in enumerate(rows):
            if vw_row.remove_button == remove_button:
                break
        else:
            return
        for control in (
            vw_row.chooser,
            vw_row.color_ctrl,
            vw_row.show_check,
            vw_row.remove_button,
        ):
            grid_sizer.Remove(control)
            control.Destroy()
        self.image.remove(vw_row.data)
        rows.remove(vw_row)
        for ii in range(i, len(rows)):
            vw_row = rows[ii]
            for j, control in enumerate(
                (
                    vw_row.chooser,
                    vw_row.color_ctrl,
                    vw_row.show_check,
                    vw_row.remove_button,
                )
            ):
                grid_sizer.SetItemPosition(control, (ii + 1, j))
        self.update_menu(self.frame.menu_subplots)
        self.layout()
        self.redraw()