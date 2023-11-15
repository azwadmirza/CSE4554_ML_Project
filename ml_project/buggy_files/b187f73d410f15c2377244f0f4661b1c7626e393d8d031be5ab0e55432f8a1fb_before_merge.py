    def _check_file(self, file_path):
        problems = []
        class_name_to_check = self.MACRO_PLUGIN_CLASS.split(".")[-1]
        with open(file_path, "r") as file_pointer:
            for line_number, line in enumerate(file_pointer, 1):
                if class_name_to_check in line:
                    problems.append(self._change_info(file_path, line_number))
        return problems