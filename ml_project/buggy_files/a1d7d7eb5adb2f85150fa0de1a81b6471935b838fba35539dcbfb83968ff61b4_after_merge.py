    def lex(self, text: Union[str, bytes], first_line: int) -> None:
        """Lexically analyze a string, storing the tokens at the tok list."""
        self.i = 0
        self.line = first_line

        if isinstance(text, bytes):
            if text.startswith(b'\xef\xbb\xbf'):
                self.enc = 'utf8'
                bom = True
            else:
                self.enc, enc_line = find_python_encoding(text, self.pyversion)
                bom = False
            try:
                decoded_text = text.decode(self.enc)
            except UnicodeDecodeError as err:
                self.report_unicode_decode_error(err, text)
                return
            except LookupError:
                self.report_unknown_encoding(enc_line)
                return
            text = decoded_text
            if bom:
                self.add_token(Bom(text[0]))
        self.s = text

        # Parse initial indent; otherwise first-line indent would not generate
        # an error.
        self.lex_indent()

        # Use some local variables as a simple optimization.
        map = self.map
        default = self.unknown_character

        # Lex the file. Repeatedly call the lexer method for the current char.
        while self.i < len(text):
            # Get the character code of the next character to lex.
            c = text[self.i]
            # Dispatch to the relevant lexer method. This will consume some
            # characters in the text, add a token to self.tok and increment
            # self.i.
            map.get(c, default)()

        # Append a break if there is no statement/block terminator at the end
        # of input.
        if len(self.tok) > 0 and (not isinstance(self.tok[-1], Break) and
                                  not isinstance(self.tok[-1], Dedent)):
            self.add_token(Break(''))

        # Attach any dangling comments/whitespace to a final Break token.
        if self.tok and isinstance(self.tok[-1], Break):
            self.tok[-1].string += self.pre_whitespace
            self.pre_whitespace = ''

        # Close remaining open blocks with Dedent tokens.
        self.lex_indent()

        self.add_token(Eof(''))