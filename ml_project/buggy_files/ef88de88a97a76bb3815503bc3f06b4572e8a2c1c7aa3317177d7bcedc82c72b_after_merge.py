    def find_s_previous_method(self, base, top):
        """
        Find the previous method based on base method
        before top method.

        This will append the method into self.pre_method1
        :param base:
        :param top:
        :return: None
        """

        method_set = self.upperFunc(base[0], base[1])

        if method_set is not None:
            if top in method_set:
                self.pre_method1.append(base)
            else:
                for item in method_set:
                    # prevent some functions from looking for themselves.
                    if item == base:
                        continue
                    self.find_s_previous_method(item, top)