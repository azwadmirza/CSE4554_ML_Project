    def get_filter_set( self, connections=None ):
        filter_set = []
        if connections:
            for oc in connections:
                for ic in oc.input_step.module.get_data_inputs():
                    if 'extensions' in ic and ic[ 'name' ] == oc.input_name:
                        filter_set += ic[ 'extensions' ]
        if not filter_set:
            filter_set = [ 'data' ]
        return ', '.join( filter_set )