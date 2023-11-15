    def _convert_lines_to_sentence(self, lines):

        sentence: Sentence = Sentence()
        for line in lines:
            # skip comments
            if self.comment_symbol is not None and line.startswith(self.comment_symbol):
                continue

            # if sentence ends, convert and return
            if self.__line_completes_sentence(line):
                if len(sentence) > 0:
                    if self.tag_to_bioes is not None:
                        sentence.convert_tag_scheme(
                            tag_type=self.tag_to_bioes, target_scheme="iobes"
                        )
                    # check if this sentence is a document boundary
                    if sentence.to_original_text() == self.document_separator_token:
                        sentence.is_document_boundary = True
                    return sentence

            # otherwise, this line is a token. parse and add to sentence
            else:
                token = self._parse_token(line)
                sentence.add_token(token)

        # check if this sentence is a document boundary
        if sentence.to_original_text() == self.document_separator_token: sentence.is_document_boundary = True

        if self.tag_to_bioes is not None:
            sentence.convert_tag_scheme(
                tag_type=self.tag_to_bioes, target_scheme="iobes"
            )

        if len(sentence) > 0: return sentence