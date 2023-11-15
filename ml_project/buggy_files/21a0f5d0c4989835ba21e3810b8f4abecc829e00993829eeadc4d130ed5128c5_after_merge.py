    def forModule(cls, name):
        """
        Return an instance of this class representing the module of the given name. If the given
        module name is "__main__", it will be translated to the actual file name of the top-level
        script without the .py or .pyc extension. This method assumes that the module with the
        specified name has already been loaded.
        """
        module = sys.modules[name]
        filePath = os.path.abspath(module.__file__)
        filePath = filePath.split(os.path.sep)
        filePath[-1], extension = os.path.splitext(filePath[-1])
        require(extension in ('.py', '.pyc'),
                'The name of a user script/module must end in .py or .pyc.')
        log.debug("Module name is %s", name)
        if name == '__main__':
            log.debug("Discovering real name of module")
            # User script/module was invoked as the main program
            if module.__package__:
                # Invoked as a module via python -m foo.bar
                log.debug("Script was invoked as a module")
                name = [filePath.pop()]
                for package in reversed(module.__package__.split('.')):
                    dirPathTail = filePath.pop()
                    assert dirPathTail == package
                    name.append(dirPathTail)
                name = '.'.join(reversed(name))
                dirPath = os.path.sep.join(filePath)
            else:
                # Invoked as a script via python foo/bar.py
                name = filePath.pop()
                dirPath = os.path.sep.join(filePath)
                cls._check_conflict(dirPath, name)
        else:
            # User module was imported. Determine the directory containing the top-level package
            for package in reversed(name.split('.')):
                dirPathTail = filePath.pop()
                assert dirPathTail == package
            dirPath = os.path.sep.join(filePath)
        log.debug("Module dir is %s", dirPath)
        require(os.path.isdir(dirPath),
                'Bad directory path %s for module %s. Note that hot-deployment does not support \
                .egg-link files yet, or scripts located in the root directory.', dirPath, name)
        fromVirtualEnv = inVirtualEnv() and dirPath.startswith(sys.prefix)
        return cls(dirPath=dirPath, name=name, fromVirtualEnv=fromVirtualEnv)