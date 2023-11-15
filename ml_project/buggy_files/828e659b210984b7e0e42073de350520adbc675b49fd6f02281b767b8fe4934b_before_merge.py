    def get_measurements(self, pipeline, object_name, category):
        if object_name == self.parent_name.value:
            if category == u"Mean_{}".format(self.sub_object_name.value):
                measurements = []

                child_columns = self.get_child_columns(pipeline)

                measurements += [column[1] for column in child_columns]

                return measurements
            elif category == "Children":
                return [u"{}_Count".format(self.sub_object_name.value)]
        elif object_name == self.sub_object_name.value and category == "Parent":
            return [self.parent_name.value]
        elif (object_name == self.sub_object_name.value and category == C_DISTANCE):
            result = []

            if self.find_parent_child_distances in (D_BOTH, D_CENTROID):
                result += ["{}_{}".format(FEAT_CENTROID, parent_name) for parent_name in self.get_parent_names()]

            if self.find_parent_child_distances in (D_BOTH, D_MINIMUM):
                result += ["{}_{}".format(FEAT_MINIMUM, parent_name) for parent_name in self.get_parent_names()]

            return result

        return []