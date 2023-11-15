    def get_trainer_program(self):
        # remove optimize ops and add a send op to main_program
        self.program.global_block().delete_ops(self.optimize_ops)
        # FIXME(typhoonzero): serialize once will fix error occurs when clone.
        self.program.__str__()
        return self.program