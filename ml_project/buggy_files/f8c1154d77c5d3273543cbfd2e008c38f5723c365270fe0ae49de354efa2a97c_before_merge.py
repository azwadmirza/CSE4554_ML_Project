    def _compare_condition(self, current_conditions, condition):
        """

        :param current_conditions:
        :param condition:
        :return:
        """

        condition_found = False

        for current_condition in current_conditions:
            if current_condition['Field'] == condition['Field'] and current_condition['Values'][0] == condition['Values'][0]:
                condition_found = True
                break

        return condition_found