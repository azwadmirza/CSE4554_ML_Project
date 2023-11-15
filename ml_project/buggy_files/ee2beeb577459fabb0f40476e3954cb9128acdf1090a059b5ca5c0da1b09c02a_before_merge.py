    def find_previous_method(self, base_method, top_method, pre_method_list):
        """
        Find the previous method based on base method before top method.
        This will append the method into pre_method_list.

        :param base_method: the base function which needs to be searched.
        :param top_method: the top-level function which calls the basic function.
        :param pre_method_list: list is used to track each function.
        :return: None
        """
        class_name, method_name = base_method
        method_set = self.apkinfo.upperfunc(class_name, method_name)

        if method_set is not None:

            if top_method in method_set:
                pre_method_list.append(base_method)
            else:
                for item in method_set:
                    # prevent some functions from looking for themselves.
                    if item == base_method:
                        continue
                    self.find_previous_method(
                        item, top_method, pre_method_list)