    def _get_cell_name(self, block):
        """Get the cell name from the block."""
        oe_data = block.userData()
        if oe_data and oe_data.oedata:
            if oe_data.oedata.has_name():
                cell_name = oe_data.oedata.def_name
            else:
                cell_name = oe_data.oedata.cell_index()
        else:
            if block.firstLineNumber() == 0:
                # There is no name for the first cell, refer by cell number
                cell_name = 0
            else:
                raise RuntimeError('Not a cell?')
        return cell_name