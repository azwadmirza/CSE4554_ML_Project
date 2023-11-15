    def createEditor(self, parent, option, index):
        """Overriding method createEditor"""
        if index.column() < 3:
            return None
        if self.show_warning(index):
            answer = QMessageBox.warning(self.parent(), _("Warning"),
                                      _("Opening this variable can be slow\n\n"
                                        "Do you want to continue anyway?"),
                                      QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.No:
                return None
        try:
            value = self.get_value(index)
            if value is None:
                return None
        except Exception as msg:
            QMessageBox.critical(self.parent(), _("Error"),
                                 _("Spyder was unable to retrieve the value of "
                                   "this variable from the console.<br><br>"
                                   "The error mesage was:<br>"
                                   "<i>%s</i>"
                                   ) % to_text_string(msg))
            return
        key = index.model().get_key(index)
        readonly = isinstance(value, tuple) or self.parent().readonly \
                   or not is_known_type(value)
        #---editor = CollectionsEditor
        if isinstance(value, (list, tuple, dict)):
            editor = CollectionsEditor()
            editor.setup(value, key, icon=self.parent().windowIcon(),
                         readonly=readonly)
            self.create_dialog(editor, dict(model=index.model(), editor=editor,
                                            key=key, readonly=readonly))
            return None
        #---editor = ArrayEditor
        elif isinstance(value, (ndarray, MaskedArray)) \
          and ndarray is not FakeObject:
            editor = ArrayEditor(parent)
            if not editor.setup_and_check(value, title=key, readonly=readonly):
                return
            self.create_dialog(editor, dict(model=index.model(), editor=editor,
                                            key=key, readonly=readonly))
            return None
        #---showing image
        elif isinstance(value, Image) and ndarray is not FakeObject \
          and Image is not FakeObject:
            arr = array(value)
            editor = ArrayEditor(parent)
            if not editor.setup_and_check(arr, title=key, readonly=readonly):
                return
            conv_func = lambda arr: Image.fromarray(arr, mode=value.mode)
            self.create_dialog(editor, dict(model=index.model(), editor=editor,
                                            key=key, readonly=readonly,
                                            conv=conv_func))
            return None
        #--editor = DataFrameEditor
        elif isinstance(value, (DataFrame, DatetimeIndex, Series)) \
          and DataFrame is not FakeObject:
            editor = DataFrameEditor()
            if not editor.setup_and_check(value, title=key):
                return
            editor.dataModel.set_format(index.model().dataframe_format)
            editor.sig_option_changed.connect(self.change_option)
            self.create_dialog(editor, dict(model=index.model(), editor=editor,
                                            key=key, readonly=readonly))
            return None
        #---editor = QDateTimeEdit
        elif isinstance(value, datetime.datetime):
            editor = QDateTimeEdit(value, parent)
            editor.setCalendarPopup(True)
            editor.setFont(get_font(font_size_delta=DEFAULT_SMALL_DELTA))
            return editor
        #---editor = QDateEdit
        elif isinstance(value, datetime.date):
            editor = QDateEdit(value, parent)
            editor.setCalendarPopup(True)
            editor.setFont(get_font(font_size_delta=DEFAULT_SMALL_DELTA))
            return editor
        #---editor = TextEditor
        elif is_text_string(value) and len(value) > 40:
            te = TextEditor(None)
            if te.setup_and_check(value):
                editor = TextEditor(value, key)
                self.create_dialog(editor, dict(model=index.model(),
                                                editor=editor, key=key,
                                                readonly=readonly))
            return None
        #---editor = QLineEdit
        elif is_editable_type(value):
            editor = QLineEdit(parent)
            editor.setFont(get_font(font_size_delta=DEFAULT_SMALL_DELTA))
            editor.setAlignment(Qt.AlignLeft)
            # This is making Spyder crash because the QLineEdit that it's
            # been modified is removed and a new one is created after
            # evaluation. So the object on which this method is trying to
            # act doesn't exist anymore.
            # editor.returnPressed.connect(self.commitAndCloseEditor)
            return editor
        #---editor = CollectionsEditor for an arbitrary object
        else:
            editor = CollectionsEditor()
            editor.setup(value, key, icon=self.parent().windowIcon(),
                         readonly=readonly)
            self.create_dialog(editor, dict(model=index.model(), editor=editor,
                                            key=key, readonly=readonly))
            return None