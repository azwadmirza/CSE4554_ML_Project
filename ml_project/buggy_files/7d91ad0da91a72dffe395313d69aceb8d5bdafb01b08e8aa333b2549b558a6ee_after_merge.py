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