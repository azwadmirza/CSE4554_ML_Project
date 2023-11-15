    def handles_nonbreaking_prefixes(self, text):
        # Splits the text into tokens to check for nonbreaking prefixes.
        tokens = text.split()
        num_tokens = len(tokens)
        for i, token in enumerate(tokens):
            # Checks if token ends with a fullstop.
            token_ends_with_period = re.search(r'^(\S+)\.$', text)
            if token_ends_with_period:
                prefix = token_ends_with_period.group(0)
                # Checks for 3 conditions if
                # i.   the prefix is a token made up of chars within the IsAlpha
                # ii.  the prefix is in the list of nonbreaking prefixes and
                #      does not contain #NUMERIC_ONLY#
                # iii. the token is not the last token and that the
                #      next token contains all lowercase.
                if ( (prefix and self.isalpha(prefix)) or
                     (prefix in self.NONBREAKING_PREFIXES and
                      prefix not in self.NUMERIC_ONLY_PREFIXES) or
                     (i != num_tokens-1 and self.islower(tokens[i+1])) ):
                    pass # No change to the token.
                # Checks if the prefix is in NUMERIC_ONLY_PREFIXES
                # and ensures that the next word is a digit.
                elif (prefix in self.NUMERIC_ONLY_PREFIXES and
                      re.search(r'^[0-9]+', token[i+1])):
                    pass # No change to the token.
                else: # Otherwise, adds a space after the tokens before a dot.
                    tokens[i] = prefix + ' .'
        return " ".join(tokens) # Stitch the tokens back.