    def init_view(self):
        '''Init the vr pane.'''
            # QWebView parts, including progress bar
        view = QtWebKitWidgets.QWebView()
        try:
            # PyQt4
            mf = view.page().mainFrame()
            mf.contentsSizeChanged.connect(self.restore_scroll_position)
        except AttributeError:
            # PyQt5
            pass
        # ToolBar parts
        self.export_button = QtWidgets.QPushButton('Export')
        self.export_button.clicked.connect(self.export)
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setIconSize(QtCore.QSize(16, 16))
        for a in (QtWebKitWidgets.QWebPage.Back, QtWebKitWidgets.QWebPage.Forward):
            self.toolbar.addAction(view.pageAction(a))
        self.toolbar.setToolTip(self.tooltip_text(
            """
            Toolbar:
            -  Navigation buttons (like a normal browser),
            -  Reload button which is used to "update" this rendering pane
            -  Options tool-button to control the way rendering is done
            -  Export button to export to the standard browser

            Keyboard shortcuts:
            <b>Ctl-C</b>  Copy html/text from the pane
            Ctl-+  Zoom in
            Ctl--  Zoom out
            Ctl-=  Zoom to original size"""         ))
        # Handle reload separately since this is used to re-render everything
        self.reload_action = view.pageAction(QtWebKitWidgets.QWebPage.Reload)
        self.reload_action.triggered.connect(self.render_delegate)
        self.toolbar.addAction(self.reload_action)
        #self.reload_action.clicked.connect(self.render)
        # Create the "Mode" toolbutton
        self.toolbutton = QtWidgets.QToolButton()
        self.toolbutton.setText('Options')
        self.toolbutton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.toolbutton.setToolTip(self.tooltip_text(
            """
            Options:
            Whole tree - Check this to render the whole tree rather than the node.
            Verbose logging - Provide more verbose logging of the rendering process.
            Auto-update - Check to automatically rerender when changes are made.
            Lock to node - Lock the rendered node/tree while another node is editted.
            Show as slideshow - Show a tree as an s5 slideshow (requires s5 support files).
            Visible code - Show the code designated by '@language' directives
            Execute code - Execute '@language' code blocks and show the output.
            Code output reST - Assume code execution text output is reStructuredText."""         ))
        self.toolbar.addWidget(self.toolbutton)
        # Add a progress bar
        self.pbar = QtWidgets.QProgressBar()
        self.pbar.setMaximumWidth(120)
        menu = QtWidgets.QMenu()

        def action(label):
            action = QtWidgets.QAction(label, self, checkable=True, triggered=self.state_change)
            menu.addAction(action)
            return action

        self.tree_mode_action = action('Whole tree')
        self.verbose_mode_action = action('Verbose logging')
        self.auto_mode_action = action('Auto-update')
        self.lock_mode_action = action('Lock to node')
        # Add an s5 option
        self.slideshow_mode_action = action('Show as slideshow')
        #self.s5_mode_action = action('s5 slideshow')
        menu.addSeparator() # Separate render mode and code options
        self.visible_code_action = action('Visible code')
        self.execute_code_action = action('Execute code')
        self.reST_code_action = action('Code outputs reST/md')
        # radio button checkables example at
        # http://stackoverflow.com/questions/10368947/how-to-make-qmenu-item-checkable-pyqt4-python
        self.toolbutton.setMenu(menu)
        # Remaining toolbar items
            #self.toolbar.addSeparator()
            #self.toolbar.addWidget(self.export_button)
        # Create the 'Export' toolbutton
        self.export_button = QtWidgets.QToolButton()
        self.export_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.export_button.setToolTip(self.tooltip_text(
            """
            Show this in the default web-browser.
            If the default browser is not already open it will be started.  Exporting
            is useful for full-screen slideshows and also for using the printing and
            saving functions of the browser."""         ))
        self.toolbar.addWidget(self.export_button)
        self.export_button.clicked.connect(self.export)
        self.export_button.setText('Export')
        #self.toolbar.addSeparator()
        # Setting visibility in toolbar is tricky, must be done throug QAction
        # http://www.qtcentre.org/threads/32437-remove-Widget-from-QToolBar
        self.pbar_action = self.toolbar.addWidget(self.pbar)
        self.pbar_action.setVisible(False)
        # Document title in toolbar
        #self.toolbar.addSeparator()
        #   spacer = QtWidgets.QWidget()
        #   spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        #   self.toolbar.addWidget(spacer)
        self.title = QtWidgets.QLabel()
        self.title.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.title.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.title.setTextFormat(1) # Set to rich text interpretation
        # None of this font stuff works! - instead I've gone for rich text above
        # font = QtGui.QFont("Sans Serif", 12, QtGui.QFont.Bold)
        #font = QtGui.QFont("Arial", 8)
        #font = QtGui.QFont()
        #font.setBold(True)
        #font.setWeight(75)
        self.toolbar.addWidget(self.title) # if needed, use 'title_action ='
        #title_action.setFont(font)  # Set font of 'QAction' rather than widget
        spacer = QtWidgets.QWidget()
        spacer.setMinimumWidth(5)
        self.toolbar.addWidget(spacer)
        # Layouts
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0) # Remove the default 11px margins
        vlayout.addWidget(self.toolbar)
        vlayout.addWidget(view)
        self.setLayout(vlayout)
        # Key shortcuts - zoom
        view.setZoomFactor(1.0) # smallish panes demand small zoom
        self.zoomIn = QtWidgets.QShortcut("Ctrl++", self, activated=lambda: view.setZoomFactor(view.zoomFactor() + .2))
        self.zoomOut = QtWidgets.QShortcut("Ctrl+-", self, activated=lambda: view.setZoomFactor(view.zoomFactor() - .2))
        self.zoomOne = QtWidgets.QShortcut("Ctrl+0", self, activated=lambda: view.setZoomFactor(0.8))
        # Some QWebView settings
        # setMaximumPagesInCache setting prevents caching of images etc.
        # pylint:disable=no-member
        if isQt5:
            pass # not ready yet.
        else:
            view.settings().setAttribute(QtWebKitWidgets.QWebSettings.PluginsEnabled, True)
        # Prevent caching, especially of images
        try:
            # PyQt4
            view.settings().setMaximumPagesInCache(0)
            view.settings().setObjectCacheCapacities(0, 0, 0)
        except AttributeError:
            # PyQt5
            pass
        #self.toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)
        # Set up other widget states
        return view