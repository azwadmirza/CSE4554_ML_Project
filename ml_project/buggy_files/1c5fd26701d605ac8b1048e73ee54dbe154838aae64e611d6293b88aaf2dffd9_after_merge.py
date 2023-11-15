    def pinfo(self,obj,oname='',formatter=None,info=None,detail_level=0):
        """Show detailed information about an object.

        Optional arguments:

        - oname: name of the variable pointing to the object.

        - formatter: special formatter for docstrings (see pdoc)

        - info: a structure with some information fields which may have been
        precomputed already.

        - detail_level: if set to 1, more information is given.
        """
        info = self.info(obj, oname=oname, formatter=formatter,
                            info=info, detail_level=detail_level)
        displayfields = []
        def add_fields(fields):
            for title, key in fields:
                field = info[key]
                if field is not None:
                    displayfields.append((title, field.rstrip()))
        
        add_fields(self.pinfo_fields1)
        
        # Base class for old-style instances
        if (not py3compat.PY3) and isinstance(obj, types.InstanceType) and info['base_class']:
            displayfields.append(("Base Class", info['base_class'].rstrip()))
        
        add_fields(self.pinfo_fields2)
        
        # Namespace
        if info['namespace'] != 'Interactive':
            displayfields.append(("Namespace", info['namespace'].rstrip()))

        add_fields(self.pinfo_fields3)
        
        # Source or docstring, depending on detail level and whether
        # source found.
        if detail_level > 0 and info['source'] is not None:
            displayfields.append(("Source", 
                                  self.format(cast_unicode(info['source']))))
        elif info['docstring'] is not None:
            displayfields.append(("Docstring", info["docstring"]))

        # Constructor info for classes
        if info['isclass']:
            if info['init_definition'] or info['init_docstring']:
                displayfields.append(("Constructor information", ""))
                if info['init_definition'] is not None:
                    displayfields.append((" Definition",
                                    info['init_definition'].rstrip()))
                if info['init_docstring'] is not None:
                    displayfields.append((" Docstring",
                                        indent(info['init_docstring'])))

        # Info for objects:
        else:
            add_fields(self.pinfo_fields_obj)

        # Finally send to printer/pager:
        if displayfields:
            page.page(self._format_fields(displayfields))