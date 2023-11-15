    def _get_cell_name(self, block):
        """Get the cell name from the block."""
        oe_data = block.userData()
        if oe_data and oe_data.oedata:
            cell_name = oe_data.oedata.def_name
        else:
            if block.firstLineNumber() == 0:
                cell_name = 'Cell at line 0'
            else:
                raise RuntimeError('Not a cell?')
        return cell_name