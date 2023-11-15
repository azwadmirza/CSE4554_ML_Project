    def detectTabbed(self, blocks):
        """ Find indented text and remove indent before further proccesing.

        Returns: a list of blocks with indentation removed.
        """
        fn_blocks = []
        while blocks:
            if blocks[0].startswith(' '*4):
                block = blocks.pop(0)
                # Check for new footnotes within this block and split at new footnote.
                m = self.RE.search(block)
                if m:
                    # Another footnote exists in this block.
                    # Any content before match is continuation of this footnote, which may be lazily indented.
                    before = block[:m.start()].rstrip('\n')
                    fn_blocks.append(self.detab(before))
                    # Add back to blocks everything from begining of match forward for next iteration.
                    blocks.insert(0, block[m.start():])
                    # End of this footnote.
                    break
                else:
                    # Entire block is part of this footnote.
                    fn_blocks.append(self.detab(block))
            else:
                # End of this footnote.
                break
        return fn_blocks