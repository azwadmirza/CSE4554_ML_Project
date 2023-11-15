    def _FreezeExecutable(self, exe):
        finder = self.finder
        finder.IncludeFile(exe.script, exe.moduleName)
        finder.IncludeFile(exe.initScript, exe.initModuleName)

        self._CopyFile(exe.base, exe.targetName, copyDependentFiles = True,
                includeMode = True)
        if self.includeMSVCR:
            self._IncludeMSVCR(exe)

        # Copy icon
        if exe.icon is not None:
            if sys.platform == "win32":
                import cx_Freeze.util
                cx_Freeze.util.AddIcon(exe.targetName, exe.icon)
            else:
                targetName = os.path.join(os.path.dirname(exe.targetName),
                        os.path.basename(exe.icon))
                self._CopyFile(exe.icon, targetName,
                        copyDependentFiles = False)

        if not os.access(exe.targetName, os.W_OK):
            mode = os.stat(exe.targetName).st_mode
            os.chmod(exe.targetName, mode | stat.S_IWUSR)
        if self.metadata is not None and sys.platform == "win32":
            self._AddVersionResource(exe.targetName)