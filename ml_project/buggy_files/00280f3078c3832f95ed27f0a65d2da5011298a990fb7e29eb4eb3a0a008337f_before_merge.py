    def __update_sub_menu(self, event, sub_menu, data):
        event.Enable(data.mode != MODE_HIDE)
        event.Text = data.name