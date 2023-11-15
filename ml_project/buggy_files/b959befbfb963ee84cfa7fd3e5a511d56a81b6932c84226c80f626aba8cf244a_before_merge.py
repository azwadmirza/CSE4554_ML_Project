    def update_current(self):
        completion_text = to_text_string(self.textedit.completion_text)
        if completion_text:
            for row, completion in enumerate(self.completion_list):
                completion_label = completion['filterText']
                if not self.case_sensitive:
                    print(completion_text)  # spyder: test-skip
                    completion_label = completion.lower()
                    completion_text = completion_text.lower()
                if completion_label.startswith(completion_text):
                    self.setCurrentRow(row)
                    self.scrollTo(self.currentIndex(),
                                  QAbstractItemView.PositionAtTop)
                    break
            # if not match:
                # self.hide()
        else:
            self.hide()