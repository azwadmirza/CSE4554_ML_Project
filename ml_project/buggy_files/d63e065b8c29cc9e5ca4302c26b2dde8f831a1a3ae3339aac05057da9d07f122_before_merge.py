    def globalize(self):
        try:
            with open(os.path.join(self.dirPath, '.original')) as f:
                return self.__class__(*json.loads(f.read()))
        except IOError as e:
            if e.errno == errno.ENOENT:
                log.warn("Can't globalize module %r.", self)
                return self
            else:
                raise