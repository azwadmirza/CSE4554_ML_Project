    def get_child_columns(self, pipeline):
        child_columns = list(filter(
            lambda column: column[0] == self.sub_object_name.value and self.should_aggregate_feature(column[1]),
            pipeline.get_measurement_columns(self)

        ))

        child_columns += self.get_child_measurement_columns(pipeline)

        return child_columns