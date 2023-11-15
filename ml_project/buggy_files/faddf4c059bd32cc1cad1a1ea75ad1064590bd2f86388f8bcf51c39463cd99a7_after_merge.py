    def addRecentProjectFile(self, projectFile):
        projectFile = QUrl(projectFile).toLocalFile()
        projects = self._recentProjectFiles()

        # remove duplicates while preserving order
        from collections import OrderedDict
        uniqueProjects = OrderedDict.fromkeys(projects)
        projects = list(uniqueProjects)
        # remove previous usage of the value
        if projectFile in uniqueProjects:
            projects.remove(projectFile)
        # add the new value in the first place
        projects.insert(0, projectFile)

        # keep only the 10 first elements
        projects = projects[0:20]

        settings = QSettings()
        settings.beginGroup("RecentFiles")
        size = settings.beginWriteArray("Projects")
        for i, p in enumerate(projects):
            settings.setArrayIndex(i)
            settings.setValue("filepath", p)
        settings.endArray()
        settings.sync()

        self.recentProjectFilesChanged.emit()