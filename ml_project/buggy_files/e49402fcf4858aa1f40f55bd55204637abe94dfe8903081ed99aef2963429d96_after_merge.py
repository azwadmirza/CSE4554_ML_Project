    def _construct_url_3(self, root, parent, obj, child_includes):
        """
        This method is used by get_url when the object is the third-level class.
        """
        root_rn = root['aci_rn']
        root_obj = root['module_object']
        parent_class = parent['aci_class']
        parent_rn = parent['aci_rn']
        parent_filter = parent['filter_target']
        parent_obj = parent['module_object']
        obj_class = obj['aci_class']
        obj_rn = obj['aci_rn']
        obj_filter = obj['filter_target']
        mo = obj['module_object']

        if not child_includes:
            self_child_includes = '&rsp-subtree=full&rsp-subtree-class=' + obj_class
        else:
            self_child_includes = '{0},{1}'.format(child_includes, obj_class)

        if not child_includes:
            parent_self_child_includes = '&rsp-subtree=full&rsp-subtree-class={0},{1}'.format(parent_class, obj_class)
        else:
            parent_self_child_includes = '{0},{1},{2}'.format(child_includes, parent_class, obj_class)

        # State is ablsent or present
        if self.module.params['state'] != 'query':
            path = 'api/mo/uni/{0}/{1}/{2}.json'.format(root_rn, parent_rn, obj_rn)
            filter_string = '?rsp-prop-include=config-only' + child_includes
        # Query for all objects of the module's class
        elif mo is None and parent_obj is None and root_obj is None:
            path = 'api/class/{0}.json'.format(obj_class)
            filter_string = ''
        # Queries when root object is provided
        elif root_obj is not None:
            # Queries when parent object is provided
            if parent_obj is not None:
                # Query for a specific object of the module's class
                if mo is not None:
                    path = 'api/mo/uni/{0}/{1}/{2}.json'.format(root_rn, parent_rn, obj_rn)
                    filter_string = ''
                # Query for all objects of the module's class that belong to a specific parent object
                else:
                    path = 'api/mo/uni/{0}/{1}.json'.format(root_rn, parent_rn)
                    filter_string = self_child_includes.replace('&', '?', 1)
            # Query for all objects of the module's class that match the provided ID value and belong to a specefic root object
            elif mo is not None:
                path = 'api/mo/uni/{0}.json'.format(root_rn)
                filter_string = '?rsp-subtree-filter={0}{1}'.format(obj_filter, self_child_includes)
            # Query for all objects of the module's class that belong to a specific root object
            else:
                path = 'api/mo/uni/{0}.json'.format(root_rn)
                filter_string = '?' + parent_self_child_includes
        # Queries when parent object is provided but root object is not provided
        elif parent_obj is not None:
            # Query for all objects of the module's class that belong to any parent class
            # matching the provided ID values for both object and parent object
            if mo is not None:
                path = 'api/class/{0}.json'.format(parent_class)
                filter_string = '?query-target-filter={0}{1}&rsp-subtree-filter={2}'.format(
                    parent_filter, self_child_includes, obj_filter)
            # Query for all objects of the module's class that belong to any parent class
            # matching the provided ID value for the parent object
            else:
                path = 'api/class/{0}.json'.format(parent_class)
                filter_string = '?query-target-filter={0}{1}'.format(parent_filter, self_child_includes)
        # Query for all objects of the module's class matching the provided ID value of the object
        else:
            path = 'api/class/{0}.json'.format(obj_class)
            filter_string = '?query-target-filter={0}'.format(obj_filter) + child_includes

        # append child_includes to filter_string if filter string is empty
        if child_includes is not None and filter_string == '':
            filter_string = child_includes.replace('&', '?', 1)

        return path, filter_string