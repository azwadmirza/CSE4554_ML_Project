    def do_compile(self):
        schema_tests = []
        for model_name, constraint_blob in self.schema.items():
            constraints = constraint_blob.get('constraints', {})
            for constraint_type, constraint_data in constraints.items():
                if constraint_data is None:
                    compiler_error(self, "no constraints given to test: '{}.{}'".format(model_name, constraint_type))
                for params in constraint_data:
                    schema_test_klass = self.get_test(constraint_type)
                    schema_test = schema_test_klass(self.project, self.og_target_dir, self.rel_filepath, model_name, params)
                    schema_tests.append(schema_test)
        return schema_tests