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
        assert extension in ('.py', '.pyc')
        if name == '__main__':
            if module.__package__:
                # invoked via python -m foo.bar
                name = [filePath.pop()]
                for package in reversed(module.__package__.split('.')):
                    dirPathTail = filePath.pop()
                    assert dirPathTail == package
                    name.append(dirPathTail)
                name = '.'.join(reversed(name))
                dirPath = os.path.sep.join(filePath)
            else:
                # invoked via python foo/bar.py
                name = filePath.pop()
                dirPath = os.path.sep.join(filePath)
                cls._check_conflict(dirPath, name)
        else:
            # imported as a module
            for package in reversed(name.split('.')):
                dirPathTail = filePath.pop()
                assert dirPathTail == package
            dirPath = os.path.sep.join(filePath)

        return cls(dirPath=dirPath, name=name)