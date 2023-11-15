    def __init__(self, qregs, cregs, instructions, plotbarriers=True,
                 line_length=None, vertical_compression='high', layout=None, initial_state=True,
                 cregbundle=False, global_phase=None):
        self.qregs = qregs
        self.cregs = cregs
        self.instructions = instructions
        self.layout = layout
        self.initial_state = initial_state

        self.cregbundle = cregbundle
        self.global_phase = global_phase
        self.plotbarriers = plotbarriers
        self.line_length = line_length
        if vertical_compression not in ['high', 'medium', 'low']:
            raise ValueError("Vertical compression can only be 'high', 'medium', or 'low'")
        self.vertical_compression = vertical_compression