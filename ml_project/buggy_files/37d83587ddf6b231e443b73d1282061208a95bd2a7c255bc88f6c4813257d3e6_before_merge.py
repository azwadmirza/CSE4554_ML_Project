    def on_token_balance_click(self, _):
        self.raise_window()
        self.deselect_all_menu_buttons()
        self.stackedWidget.setCurrentIndex(PAGE_TRUST)
        self.trust_page.load_trust_statistics()
        self.navigation_stack = []
        self.hide_left_menu_playlist()