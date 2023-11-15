    def keypress(self, key, editor):
        if key in "rRe":
            signals.status_message.send(
                self,
                message="Press enter to edit this field.",
                expire=1000
            )
            return
        elif key == "m_select":
            self.subeditor.grideditor = editor
            editor.master.switch_view("edit_focus_setcookie_attrs")
        else:
            return key