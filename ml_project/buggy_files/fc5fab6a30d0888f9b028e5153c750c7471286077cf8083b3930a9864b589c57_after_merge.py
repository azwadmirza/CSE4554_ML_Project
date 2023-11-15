    def tab_changed(self, index):
        if index == 0:
            self.load_general_tab()
        elif index == 1:
            self.load_requests_tab()
        elif index == 2:
            self.load_trustchain_tab()
        elif index == 3:
            self.dispersy_tab_changed(self.window().dispersy_tab_widget.currentIndex())
        elif index == 4:
            self.load_events_tab()
        elif index == 5:
            self.system_tab_changed(self.window().system_tab_widget.currentIndex())
        elif index == 6:
            self.load_logs_tab()