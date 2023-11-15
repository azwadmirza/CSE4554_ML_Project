    def createEditor(self, parent, option, index, object_explorer=False):
        """Overriding method createEditor"""
        val_type = index.sibling(index.row(), 1).data()
        self.sig_open_editor.emit()
        if index.column() < 3:
            return None
        if self.show_warning(index):
            answer = QMessageBox.warning(
                self.parent(), _("Warning"),
                _("Opening this variable can be slow\n\n"
                  "Do you want to continue anyway?"),
                QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.No:
                return None
        try:
            value = self.get_value(index)
            if value is None:
                return None
        except ImportError as msg:
            self.sig_editor_shown.emit()
            module = str(msg).split("'")[1]
            if module in ['pandas', 'numpy']:
                if module == 'numpy':
                    val_type = 'array'
                else:
                    val_type = 'dataframe, series'
                QMessageBox.critical(
                    self.parent(), _("Error"),
                    _("Spyder is unable to show the {val_type} or object "
                      "you're trying to view because <tt>{module}</tt> was "
                      "not installed alongside Spyder. Please install "
                      "this package in your Spyder environment."
                      "<br>").format(val_type=val_type, module=module))
                return
            else:
                QMessageBox.critical(
                    self.parent(), _("Error"),
                    _("Spyder is unable to show the variable you're "
                      "trying to view because the module "
                      "<tt>{module}</tt> was not found in your  "
                      "Spyder environment. Please install "
                      "this package in your Spyder environment."
                      "<br>").format(module=module))
                return
        except Exception as msg:
            QMessageBox.critical(
                self.parent(), _("Error"),
                _("Spyder was unable to retrieve the value of "
                  "this variable from the console.<br><br>"
                  "The error message was:<br>"
                  "%s") % to_text_string(msg))
            return

        key = index.model().get_key(index)
        readonly = (isinstance(value, (tuple, set)) or self.parent().readonly
                    or not is_known_type(value))
        # CollectionsEditor for a list, tuple, dict, etc.
        if isinstance(value, (list, set, tuple, dict)) and not object_explorer:
            from spyder.widgets.collectionseditor import CollectionsEditor
            editor = CollectionsEditor(parent=parent)
            editor.setup(value, key, icon=self.parent().windowIcon(),
                         readonly=readonly)
            self.create_dialog(editor, dict(model=index.model(), editor=editor,
                                            key=key, readonly=readonly))
            return None
        # ArrayEditor for a Numpy array
        elif (isinstance(value, (ndarray, MaskedArray)) and
                ndarray is not FakeObject and not object_explorer):
            editor = ArrayEditor(parent=parent)
            if not editor.setup_and_check(value, title=key, readonly=readonly):
                return
            self.create_dialog(editor, dict(model=index.model(), editor=editor,
                                            key=key, readonly=readonly))
            return None
        # ArrayEditor for an images
        elif (isinstance(value, Image) and ndarray is not FakeObject and
                Image is not FakeObject and not object_explorer):
            arr = array(value)
            editor = ArrayEditor(parent=parent)
            if not editor.setup_and_check(arr, title=key, readonly=readonly):
                return
            conv_func = lambda arr: Image.fromarray(arr, mode=value.mode)
            self.create_dialog(editor, dict(model=index.model(), editor=editor,
                                            key=key, readonly=readonly,
                                            conv=conv_func))
            return None
        # DataFrameEditor for a pandas dataframe, series or index
        elif (isinstance(value, (DataFrame, Index, Series))
                and DataFrame is not FakeObject and not object_explorer):
            editor = DataFrameEditor(parent=parent)
            if not editor.setup_and_check(value, title=key):
                return
            editor.dataModel.set_format(index.model().dataframe_format)
            editor.sig_option_changed.connect(self.change_option)
            self.create_dialog(editor, dict(model=index.model(), editor=editor,
                                            key=key, readonly=readonly))
            return None
        # QDateEdit and QDateTimeEdit for a dates or datetime respectively
        elif isinstance(value, datetime.date) and not object_explorer:
            # Needed to handle NaT values
            # See spyder-ide/spyder#8329
            try:
                value.time()
            except ValueError:
                self.sig_editor_shown.emit()
                return None
            if readonly:
                self.sig_editor_shown.emit()
                return None
            else:
                if isinstance(value, datetime.datetime):
                    editor = QDateTimeEdit(value, parent=parent)
                else:
                    editor = QDateEdit(value, parent=parent)
                editor.setCalendarPopup(True)
                editor.setFont(get_font(font_size_delta=DEFAULT_SMALL_DELTA))
                self.sig_editor_shown.emit()
                return editor
        # TextEditor for a long string
        elif is_text_string(value) and len(value) > 40 and not object_explorer:
            te = TextEditor(None, parent=parent)
            if te.setup_and_check(value):
                editor = TextEditor(value, key,
                                    readonly=readonly, parent=parent)
                self.create_dialog(editor, dict(model=index.model(),
                                                editor=editor, key=key,
                                                readonly=readonly))
            return None
        # QLineEdit for an individual value (int, float, short string, etc)
        elif is_editable_type(value) and not object_explorer:
            if readonly:
                self.sig_editor_shown.emit()
                return None
            else:
                editor = QLineEdit(parent=parent)
                editor.setFont(get_font(font_size_delta=DEFAULT_SMALL_DELTA))
                editor.setAlignment(Qt.AlignLeft)
                # This is making Spyder crash because the QLineEdit that it's
                # been modified is removed and a new one is created after
                # evaluation. So the object on which this method is trying to
                # act doesn't exist anymore.
                # editor.returnPressed.connect(self.commitAndCloseEditor)
                self.sig_editor_shown.emit()
                return editor
        # ObjectExplorer for an arbitrary Python object
        else:
            show_callable_attributes = index.model().show_callable_attributes
            show_special_attributes = index.model().show_special_attributes
            dataframe_format = index.model().dataframe_format

            if show_callable_attributes is None:
                show_callable_attributes = False
            if show_special_attributes is None:
                show_special_attributes = False

            from spyder.plugins.variableexplorer.widgets.objectexplorer \
                import ObjectExplorer
            editor = ObjectExplorer(
                value,
                name=key,
                parent=parent,
                show_callable_attributes=show_callable_attributes,
                show_special_attributes=show_special_attributes,
                dataframe_format=dataframe_format,
                readonly=readonly)
            editor.sig_option_changed.connect(self.change_option)
            self.create_dialog(editor, dict(model=index.model(),
                                            editor=editor,
                                            key=key, readonly=readonly))
            return None