    def get_categories(self, pipeline, object_name):
        all_object_names = [operand.operand_objects.value
                            for operand in self.get_operands()
                            if operand.object != cpmeas.IMAGE]
        if len(all_object_names):
            if object_name in all_object_names:
                return [C_MATH]
        elif object_name == cpmeas.IMAGE:
            return [C_MATH]
        return []