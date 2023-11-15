    def on_page_back_clicked(self):
        try:
            prev_page = self.navigation_stack.pop()
            self.stackedWidget.setCurrentIndex(prev_page)
            if prev_page == PAGE_SEARCH_RESULTS:
                self.stackedWidget.widget(prev_page).load_search_results_in_list()
            if prev_page == PAGE_SUBSCRIBED_CHANNELS:
                self.stackedWidget.widget(prev_page).load_subscribed_channels()
            if prev_page == PAGE_DISCOVERED:
                self.stackedWidget.widget(prev_page).load_discovered_channels()
        except IndexError:
            logging.exception("Unknown page found in stack")