    def __init__(self, parent, exception_text, tribler_version):
        QDialog.__init__(self, parent)

        uic.loadUi(get_ui_file_path('feedback_dialog.ui'), self)

        self.setWindowTitle("Unexpected error")
        self.selected_item_index = 0
        self.tribler_version = tribler_version
        self.request_mgr = None

        # Qt 5.2 does not have the setPlaceholderText property
        if hasattr(self.comments_text_edit, "setPlaceholderText"):
            self.comments_text_edit.setPlaceholderText("Comments (optional)")

        def add_item_to_info_widget(key, value):
            item = QTreeWidgetItem(self.env_variables_list)
            item.setText(0, key)
            item.setText(1, value)

        self.error_text_edit.setPlainText(exception_text.rstrip())

        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.send_report_button.clicked.connect(self.on_send_clicked)

        # Add machine information to the tree widget
        add_item_to_info_widget('os.getcwd', '%s' % os.getcwd())
        add_item_to_info_widget('sys.executable', '%s' % sys.executable)

        add_item_to_info_widget('os', os.name)
        add_item_to_info_widget('platform', sys.platform)
        add_item_to_info_widget('platform.details', platform.platform())
        add_item_to_info_widget('platform.machine', platform.machine())
        add_item_to_info_widget('python.version', sys.version)
        add_item_to_info_widget('indebug', str(__debug__))

        for argv in sys.argv:
            add_item_to_info_widget('sys.argv', '%s' % argv)

        for path in sys.path:
            add_item_to_info_widget('sys.path', '%s' % path)

        for key in os.environ.keys():
            add_item_to_info_widget('os.environ', '%s: %s' % (key, os.environ[key]))

        request_ind = 1
        for endpoint, method, data, timestamp, status_code in sorted(tribler_performed_requests.values(),
                                                                     key=lambda x: x[3])[-10:]:
            add_item_to_info_widget('request_%d' % request_ind, '%s %s %s (time: %s, code: %s)' %
                                    (endpoint, method, data, timestamp, status_code))
            request_ind += 1

        # Users can remove specific lines in the report
        self.env_variables_list.customContextMenuRequested.connect(self.on_right_click_item)