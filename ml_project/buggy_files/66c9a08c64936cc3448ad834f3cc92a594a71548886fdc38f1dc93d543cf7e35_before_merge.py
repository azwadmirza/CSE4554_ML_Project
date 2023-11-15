    def run(self, lines):
        text = "\n".join(lines)
        new_blocks = []
        text = text.rsplit("\n\n")
        items = []
        left_tag = ''
        right_tag = ''
        in_tag = False  # flag

        while text:
            block = text[0]
            if block.startswith("\n"):
                block = block[1:]
            text = text[1:]

            if block.startswith("\n"):
                block = block[1:]

            if not in_tag:
                if block.startswith("<") and len(block.strip()) > 1:

                    if block[1:4] == "!--":
                        # is a comment block
                        left_tag, left_index, attrs = "--", 2, {}
                    else:
                        left_tag, left_index, attrs = self._get_left_tag(block)
                    right_tag, data_index = self._get_right_tag(left_tag,
                                                                left_index,
                                                                block)
                    # keep checking conditions below and maybe just append

                    if data_index < len(block) and (self.md.is_block_level(left_tag) or left_tag == '--'):
                        text.insert(0, block[data_index:])
                        block = block[:data_index]

                    if not (self.md.is_block_level(left_tag) or block[1] in ["!", "?", "@", "%"]):
                        new_blocks.append(block)
                        continue

                    if self._is_oneliner(left_tag):
                        new_blocks.append(block.strip())
                        continue

                    if block.rstrip().endswith(">") \
                            and self._equal_tags(left_tag, right_tag):
                        if self.markdown_in_raw and 'markdown' in attrs.keys():
                            block = block[left_index:-len(right_tag) - 2]
                            new_blocks.append(self.md.htmlStash.
                                              store_tag(left_tag, attrs, 0, 2))
                            new_blocks.extend([block])
                        else:
                            new_blocks.append(
                                self.md.htmlStash.store(block.strip()))
                        continue
                    else:
                        # if is block level tag and is not complete
                        if (not self._equal_tags(left_tag, right_tag)) and \
                           (self.md.is_block_level(left_tag) or left_tag == "--"):
                            items.append(block.strip())
                            in_tag = True
                        else:
                            new_blocks.append(
                                self.md.htmlStash.store(block.strip())
                            )
                        continue

                else:
                    new_blocks.append(block)

            else:
                items.append(block)

                # Need to evaluate all items so we can calculate relative to the left index.
                right_tag, data_index = self._get_right_tag(left_tag, left_index, ''.join(items))
                # Adjust data_index: relative to items -> relative to last block
                prev_block_length = 0
                for item in items[:-1]:
                    prev_block_length += len(item)
                data_index -= prev_block_length

                if self._equal_tags(left_tag, right_tag):
                    # if find closing tag

                    if data_index < len(block):
                        # we have more text after right_tag
                        items[-1] = block[:data_index]
                        text.insert(0, block[data_index:])

                    in_tag = False
                    if self.markdown_in_raw and 'markdown' in attrs.keys():
                        items[0] = items[0][left_index:]
                        items[-1] = items[-1][:-len(right_tag) - 2]
                        if items[len(items) - 1]:  # not a newline/empty string
                            right_index = len(items) + 3
                        else:
                            right_index = len(items) + 2
                        new_blocks.append(self.md.htmlStash.store_tag(
                            left_tag, attrs, 0, right_index))
                        placeholderslen = len(self.md.htmlStash.tag_data)
                        new_blocks.extend(
                            self._nested_markdown_in_html(items))
                        nests = len(self.md.htmlStash.tag_data) - \
                            placeholderslen
                        self.md.htmlStash.tag_data[-1 - nests][
                            'right_index'] += nests - 2
                    else:
                        new_blocks.append(
                            self.md.htmlStash.store('\n\n'.join(items)))
                    items = []

        if items:
            if self.markdown_in_raw and 'markdown' in attrs.keys():
                items[0] = items[0][left_index:]
                items[-1] = items[-1][:-len(right_tag) - 2]
                if items[len(items) - 1]:  # not a newline/empty string
                    right_index = len(items) + 3
                else:
                    right_index = len(items) + 2
                new_blocks.append(
                    self.md.htmlStash.store_tag(
                        left_tag, attrs, 0, right_index))
                placeholderslen = len(self.md.htmlStash.tag_data)
                new_blocks.extend(self._nested_markdown_in_html(items))
                nests = len(self.md.htmlStash.tag_data) - placeholderslen
                self.md.htmlStash.tag_data[-1 - nests][
                    'right_index'] += nests - 2
            else:
                new_blocks.append(
                    self.md.htmlStash.store('\n\n'.join(items)))
            new_blocks.append('\n')

        new_text = "\n\n".join(new_blocks)
        return new_text.split("\n")