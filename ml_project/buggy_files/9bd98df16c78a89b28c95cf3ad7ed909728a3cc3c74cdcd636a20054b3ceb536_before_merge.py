    def get(self, key=None, default=None, category=None, return_obj=False,
            strattr=False, raise_exception=False, accessing_obj=None,
            default_access=True, return_list=False):
        """
        Get the Attribute.

        Args:
            key (str or list, optional): the attribute identifier or
                multiple attributes to get. if a list of keys, the
                method will return a list.
            category (str, optional): the category within which to
                retrieve attribute(s).
            default (any, optional): The value to return if an
                Attribute was not defined. If set, it will be returned in
                a one-item list.
            return_obj (bool, optional): If set, the return is not the value of the
                Attribute but the Attribute object itself.
            strattr (bool, optional): Return the `strvalue` field of
                the Attribute rather than the usual `value`, this is a
                string-only value for quick database searches.
            raise_exception (bool, optional): When an Attribute is not
                found, the return from this is usually `default`. If this
                is set, an exception is raised instead.
            accessing_obj (object, optional): If set, an `attrread`
                permission lock will be checked before returning each
                looked-after Attribute.
            default_access (bool, optional): If no `attrread` lock is set on
                object, this determines if the lock should then be passed or not.
            return_list (bool, optional):

        Returns:
            result (any or list): One or more matches for keys and/or categories. Each match will be
                the value of the found Attribute(s) unless `return_obj` is True, at which point it
                will be the attribute object itself or None. If `return_list` is True, this will
                always be a list, regardless of the number of elements.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key`.

        """

        class RetDefault(object):
            """Holds default values"""

            def __init__(self):
                self.key = None
                self.value = default
                self.category = None
                self.strvalue = str(default) if default is not None else None

        ret = []
        for keystr in make_iter(key):
            # it's okay to send a None key
            attr_objs = self._getcache(keystr, category)
            if attr_objs:
                ret.extend(attr_objs)
            elif raise_exception:
                raise AttributeError
            elif return_obj:
                ret.append(None)
            else:
                ret.append(RetDefault())

        if accessing_obj:
            # check 'attrread' locks
            ret = [attr for attr in ret if attr.access(accessing_obj,
                                                       self._attrread, default=default_access)]
        if strattr:
            ret = ret if return_obj else [attr.strvalue for attr in ret if attr]
        else:
            ret = ret if return_obj else [attr.value for attr in ret if attr]

        if return_list:
            return ret if ret else [default] if default is not None else []
        elif not ret:
            return ret if len(key) > 1 else default
        return ret[0] if len(ret) == 1 else ret