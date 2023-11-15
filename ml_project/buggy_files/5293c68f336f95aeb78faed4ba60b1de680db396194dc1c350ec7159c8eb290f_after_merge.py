    def shrink_offset_pairs(self):
        """Lower any two blocks offset from each other the same ammount.

        Before this shrink pass, two blocks explicitly offset from each
        other would not get minimized properly:
         >>> b = st.integers(0, 255)
         >>> find(st.tuples(b, b), lambda x: x[0] == x[1] + 1)
        (149,148)

        This expensive (O(n^2)) pass goes through every pair of non-zero
        blocks in the current shrink target and sees if the shrink
        target can be improved by applying an offset to both of them.
        """
        self.debug('Shrinking offset pairs.')

        current = [self.shrink_target.buffer[u:v] for u, v in self.blocks]

        def int_from_block(i):
            return int_from_bytes(current[i])

        def block_len(i):
            u, v = self.blocks[i]
            return v - u

        # Try reoffseting every pair
        def reoffset_pair(pair, o):
            n = len(self.blocks)
            # Number of blocks may have changed, need to validate
            valid_pair = [
                p for p in pair if p < n and int_from_block(p) > 0 and
                self.is_payload_block(p)
            ]

            if len(valid_pair) < 2:
                return

            m = min([int_from_block(p) for p in valid_pair])

            new_blocks = [self.shrink_target.buffer[u:v]
                          for u, v in self.blocks]
            for i in valid_pair:
                new_blocks[i] = int_to_bytes(
                    int_from_block(i) + o - m, block_len(i))
            buffer = hbytes().join(new_blocks)
            return self.incorporate_new_buffer(buffer)

        i = 0
        while i < len(self.blocks):
            if self.is_payload_block(i) and int_from_block(i) > 0:
                j = i + 1
                while j < len(self.shrink_target.blocks):
                    block_val = int_from_block(j)
                    i_block_val = int_from_block(i)
                    if self.is_payload_block(j) \
                       and block_val > 0 and i_block_val > 0:
                        offset = min(int_from_block(i),
                                     int_from_block(j))
                        # Save current before shrinking
                        current = [self.shrink_target.buffer[u:v]
                                   for u, v in self.blocks]
                        minimize_int(
                            offset, lambda o: reoffset_pair((i, j), o))
                    j += 1
            i += 1