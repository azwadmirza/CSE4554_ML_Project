    def update_current(self):
        completion_text = to_text_string(
                self.textedit.get_current_word(completion=True))
        if completion_text:
            for row, completion in enumerate(self.completion_list):
                if not self.is_internal_console:
                    completion_label = completion['filterText']
                else:
                    completion_label = completion[0]

                if completion_label.startswith(completion_text):
                    self.setCurrentRow(row)
                    self.scrollTo(self.currentIndex(),
                                  QAbstractItemView.PositionAtTop)
                    break
        else:
            self.hide()