    def __init__(self, loop_nests, init_block, loop_body, loc, array_analysis, index_var):
        super(Parfor, self).__init__(
            op   = 'parfor',
            loc  = loc
        )

        self.id = type(self).id_counter
        type(self).id_counter =+ 1
        #self.input_info  = input_info
        #self.output_info = output_info
        self.loop_nests = loop_nests
        self.init_block = init_block
        self.loop_body = loop_body
        self.array_analysis = array_analysis
        self.index_var = index_var