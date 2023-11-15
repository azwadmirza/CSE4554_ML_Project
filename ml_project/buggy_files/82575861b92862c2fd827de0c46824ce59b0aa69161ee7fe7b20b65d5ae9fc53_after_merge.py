    def md_to_html(self, p):
        '''Convert p.b to html using markdown.'''
        c, pc = self.c, self.pc
        mf = self.view.page().mainFrame()
        path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.chdir(path)
        # Need to save position of last node before rendering
        ps = mf.scrollBarValue(QtCore.Qt.Vertical)
        pc.scrollbar_pos_dict[self.last_node.v] = ps
        # Which node should be rendered?
        if self.lock_mode:
            # use locked node for position to be rendered.
            self.pr = self.plock
        else:
            # use new current node, whether changed or not.
            self.pr = c.p # use current node
        self.last_node = self.pr.copy()
            # Store this node as last node rendered
        # Set the node header in the toolbar.
        self.title.setText('' if self.s else '<b>' + self.pr.h + '</b>')
        if not self.auto:
            self.pbar.setValue(0)
            self.pbar_action.setVisible(True)
        # Handle all the nodes in the tree.
        html = self.md_process_nodes(self.pr, tree=self.tree)
        if not self.auto:
            self.pbar.setValue(50)
        self.app.processEvents()
            # Apparently this can't be done in docutils.
        try:
            # Call markdown to get the string.
            mdext = c.config.getString('view-rendered-md-extensions') or 'extra'
            mdext = [x.strip() for x in mdext.split(',')]
            if pygments:
                mdext.append('codehilite')
            html = markdown(html, mdext)
            
            # tbp: this is a kludge to change the background color
            # of the rendering pane.  Markdown does not emit
            # a css style sheet, but the browser will apply
            # a style element at the top of the page to the
            # whole page. MD_RENDERING_BG_COLOR is a global
            # variable set during the config process.
            html = '<style type="text/css">body{background-color:%s;}</style>\n' %(MD_RENDERING_BG_COLOR) + html
            
            return g.toUnicode(html)
        except Exception as e:
            print(e)
            return 'Markdown error... %s' % e