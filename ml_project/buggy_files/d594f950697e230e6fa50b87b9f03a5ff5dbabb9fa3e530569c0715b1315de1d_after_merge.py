    def setup_project(self, directory):
        """Setup project"""
        self.emptywidget.hide()
        self.treewidget.show()

        # Setup the directory shown by the tree
        self.set_project_dir(directory)