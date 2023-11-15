    def set_value(self, val):
        raise RuntimeError(textwrap.dedent(
            """\
            Block components do not support assignment or set_value().
            Use the transfer_attributes_from() method to transfer the
            components and public attributes from one block to another:
                model.b[1].transfer_attributes_from(other_block)
            """))