        def core(typ):
            for attrinfo in self._get_attribute_templates(typ):
                ret = attrinfo.resolve(typ, attr)
                if ret is not None:
                    return ret