    def add_directive_header(self, sig: str) -> None:
        super().add_directive_header(sig)
        sourcename = self.get_sourcename()
        if not self.options.annotation:
            # obtain type annotation for this attribute
            try:
                annotations = get_type_hints(self.parent)
            except TypeError:
                annotations = {}
            except KeyError:
                # a broken class found (refs: https://github.com/sphinx-doc/sphinx/issues/8084)
                annotations = {}
            except AttributeError:
                # AttributeError is raised on 3.5.2 (fixed by 3.5.3)
                annotations = {}

            if self.objpath[-1] in annotations:
                objrepr = stringify_typehint(annotations.get(self.objpath[-1]))
                self.add_line('   :type: ' + objrepr, sourcename)
            else:
                key = ('.'.join(self.objpath[:-1]), self.objpath[-1])
                if self.analyzer and key in self.analyzer.annotations:
                    self.add_line('   :type: ' + self.analyzer.annotations[key],
                                  sourcename)

            # data descriptors do not have useful values
            if not self._datadescriptor:
                try:
                    if self.object is INSTANCEATTR:
                        pass
                    else:
                        objrepr = object_description(self.object)
                        self.add_line('   :value: ' + objrepr, sourcename)
                except ValueError:
                    pass
        elif self.options.annotation is SUPPRESS:
            pass
        else:
            self.add_line('   :annotation: %s' % self.options.annotation, sourcename)