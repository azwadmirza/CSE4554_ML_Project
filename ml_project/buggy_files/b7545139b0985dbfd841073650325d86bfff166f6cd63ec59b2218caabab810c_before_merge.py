    def keypress(self, key, editor):
        if key in "rRe":
            signals.status_message.send(
                self,
                message="Press enter to edit this field.",
                expire=1000
            )
            return
        elif key == "m_select":
            editor.master.view_grideditor(
                self.subeditor(
                    editor.master,
                    editor.walker.get_current_value(),
                    editor.set_subeditor_value,
                    editor.walker.focus,
                    editor.walker.focus_col
                )
            )
        else:
            return key