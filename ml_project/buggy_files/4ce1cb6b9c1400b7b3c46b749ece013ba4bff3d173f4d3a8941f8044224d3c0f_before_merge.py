    def get_measurement_columns(self, pipeline):
        all_object_names = list(set([operand.operand_objects.value
                                     for operand in self.operands
                                     if operand.object != cpmeas.IMAGE]))
        if len(all_object_names):
            return [(name, self.measurement_name(), cpmeas.COLTYPE_FLOAT)
                    for name in all_object_names]
        else:
            return [(cpmeas.IMAGE, 
                     self.measurement_name(), 
                     cpmeas.COLTYPE_FLOAT)]