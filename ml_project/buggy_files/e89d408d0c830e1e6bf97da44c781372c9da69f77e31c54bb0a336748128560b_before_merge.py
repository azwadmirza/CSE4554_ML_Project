    def item_selected(self, item=None):
        if item is None:
            item = self.currentItem()
        # index = self.currentIndex()
        # self.textedit.show_calltip()
        self.textedit.insert_completion(to_text_string(item.text()))
        self.hide()