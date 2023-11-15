    def get_categories(self, pipeline, object_name):
        if object_name == self.x_name.value:
            if self.wants_per_parent_means:
                return [
                    "Mean_{}".format(self.y_name),
                    "Children"
                ]
            else:
                return ["Children"]
        elif object_name == self.y_name.value:
            result = ["Parent"]

            if self.find_parent_child_distances != D_NONE:
                result += [C_DISTANCE]

            return result

        return []