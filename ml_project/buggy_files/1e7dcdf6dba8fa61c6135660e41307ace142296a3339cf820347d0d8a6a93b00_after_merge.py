    def fix_indent(self, forward=True, comment_or_string=False):
        """
        Fix indentation (Python only, no text selection)
        forward=True: fix indent only if text is not enough indented
                      (otherwise force indent)
        forward=False: fix indent only if text is too much indented
                       (otherwise force unindent)

        Returns True if indent needed to be fixed
        """
        if not self.is_python_like():
            return
        cursor = self.textCursor()
        block_nb = cursor.blockNumber()
        # find the line that contains our scope
        diff = 0
        add_indent = False
        prevline = None
        for prevline in range(block_nb-1, -1, -1):
            cursor.movePosition(QTextCursor.PreviousBlock)
            prevtext = to_text_string(cursor.block().text()).rstrip()
            if not prevtext.strip().startswith('#'):
                if prevtext.strip().endswith(')'):
                    comment_or_string = True  # prevent further parsing
                elif prevtext.strip().endswith(':'):
                    add_indent = True
                    comment_or_string = True
                if prevtext.count(')') > prevtext.count('('):
                    diff = prevtext.count(')') - prevtext.count('(')
                    continue
                elif diff:
                    diff += prevtext.count(')') - prevtext.count('(')
                    if not diff:
                        break
                else:
                    break

        indent = self.get_block_indentation(block_nb)
        
        if not prevline:
            return False

        correct_indent = self.get_block_indentation(prevline)

        if add_indent:
            correct_indent += len(self.indent_chars)

        if not comment_or_string:
            if prevtext.endswith(':'):
                # Indent
                correct_indent += len(self.indent_chars)
            elif prevtext.endswith('continue') or prevtext.endswith('break') \
              or prevtext.endswith('pass'):
                # Unindent
                correct_indent -= len(self.indent_chars)
            elif prevtext.endswith(',') \
              and len(re.split(r'\(|\{|\[', prevtext)) > 1:
                rlmap = {")":"(", "]":"[", "}":"{"}
                for par in rlmap:
                    i_right = prevtext.rfind(par)
                    if i_right != -1:
                        prevtext = prevtext[:i_right]
                        for _i in range(len(prevtext.split(par))):
                            i_left = prevtext.rfind(rlmap[par])
                            if i_left != -1:
                                prevtext = prevtext[:i_left]
                            else:
                                break
                else:
                    if prevtext.strip():
                        prevexpr = re.split(r'\(|\{|\[', prevtext)[-1]
                        correct_indent = len(prevtext)-len(prevexpr)
                    else:
                        correct_indent = len(prevtext)

        if (forward and indent >= correct_indent) or \
           (not forward and indent <= correct_indent):
            # No indentation fix is necessary
            return False

        if correct_indent >= 0:
            cursor = self.textCursor()
            cursor.beginEditBlock()
            cursor.movePosition(QTextCursor.StartOfBlock)
            cursor.setPosition(cursor.position()+indent, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.insertText(self.indent_chars[0]*correct_indent)
            cursor.endEditBlock()
            return True