    def focus_changed(self):
        if self.master.view.focus.flow:
            self.tabs = [
                (self.tab_request, self.view_request),
                (self.tab_response, self.view_response),
                (self.tab_details, self.view_details),
            ]
            self.show()
        else:
            self.master.window.pop()