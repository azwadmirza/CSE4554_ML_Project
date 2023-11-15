    def is_aggregation_module(self):
        '''Need to run all cycles in same worker if across cycles'''
        return self.tile_method == T_ACROSS_CYCLES