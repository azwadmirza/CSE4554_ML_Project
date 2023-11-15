    def tokenize(self, tokens, return_str=False):
        """
        Python port of the Moses detokenizer.
        
        :param tokens: A list of strings, i.e. tokenized text.
        :type tokens: list(str)
        :return: str
        """
        # Convert the list of tokens into a string and pad it with spaces.
        text = u" {} ".format(" ".join(tokens))
        # Converts input string into unicode.
        text = text_type(text)
        # Detokenize the agressive hyphen split.
        regexp, subsitution = self.AGGRESSIVE_HYPHEN_SPLIT
        text = re.sub(regexp, subsitution, text)
        # Unescape the XML symbols.
        text = self.unescape_xml(text)
        # Keep track of no. of quotation marks.
        quote_counts = {u"'":0 , u'"':0, u"``":0, u"`":0, u"''":0}
        
        # The *prepend_space* variable is used to control the "effects" of 
        # detokenization as the function loops through the list of tokens and
        # changes the *prepend_space* accordingly as it sequentially checks 
        # through the language specific and language independent conditions. 
        prepend_space = " " 
        detokenized_text = "" 
        tokens = text.split()
        # Iterate through every token and apply language specific detokenization rule(s).
        for i, token in enumerate(iter(tokens)):
            # Check if the first char is CJK.
            if is_cjk(token[0]):
                # Perform left shift if this is a second consecutive CJK word.
                if i > 0 and is_cjk(token[-1]):
                    detokenized_text += token
                # But do nothing special if this is a CJK word that doesn't follow a CJK word
                else:
                    detokenized_text += prepend_space + token
                prepend_space = " " 
                
            # If it's a currency symbol.
            elif token in self.IsSc:
                # Perform right shift on currency and other random punctuation items
                detokenized_text += prepend_space + token
                prepend_space = ""

            elif re.match(r'^[\,\.\?\!\:\;\\\%\}\]\)]+$', token):
                # In French, these punctuations are prefixed with a non-breakable space.
                if self.lang == 'fr' and re.match(r'^[\?\!\:\;\\\%]$', token):
                    detokenized_text += " "
                # Perform left shift on punctuation items.
                detokenized_text += token
                prepend_space = " " 
               
            elif (self.lang == 'en' and i > 0 
                  and re.match(u'^[\'][{}]'.format(self.IsAlpha), token)
                  and re.match(u'[{}]'.format(self.IsAlnum), token)):
                # For English, left-shift the contraction.
                detokenized_text += token
                prepend_space = " "
                
            elif (self.lang == 'cs' and i > 1
                  and re.match(r'^[0-9]+$', tokens[-2]) # If the previous previous token is a number.
                  and re.match(r'^[.,]$', tokens[-1]) # If previous token is a dot.
                  and re.match(r'^[0-9]+$', token)): # If the current token is a number.
                # In Czech, left-shift floats that are decimal numbers.
                detokenized_text += token
                prepend_space = " "
            
            elif (self.lang in ['fr', 'it'] and i <= len(tokens)-2
                  and re.match(u'[{}][\']$'.format(self.IsAlpha), token)
                  and re.match(u'^[{}]$'.format(self.IsAlpha), tokens[i+1])): # If the next token is alpha.
                # For French and Italian, right-shift the contraction.
                detokenized_text += prepend_space + token
                prepend_space = ""
            
            elif (self.lang == 'cs' and i <= len(tokens)-3
                  and re.match(u'[{}][\']$'.format(self.IsAlpha), token)
                  and re.match(u'^[-–]$', tokens[i+1])
                  and re.match(u'^li$|^mail.*', tokens[i+2], re.IGNORECASE)): # In Perl, ($words[$i+2] =~ /^li$|^mail.*/i)
                # In Czech, right-shift "-li" and a few Czech dashed words (e.g. e-mail)
                detokenized_text += prepend_space + token + tokens[i+1]
                next(tokens, None) # Advance over the dash
                prepend_space = ""
                
            # Combine punctuation smartly.
            elif re.match(r'''^[\'\"„“`]+$''', token):
                normalized_quo = token
                if re.match(r'^[„“”]+$', token):
                    normalized_quo = '"'
                quote_counts.get(normalized_quo, 0)
                
                if self.lang == 'cs' and token == u"„":
                    quote_counts[normalized_quo] = 0
                if self.lang == 'cs' and token == u"“":
                    quote_counts[normalized_quo] = 1
            
            
                if quote_counts[normalized_quo] % 2 == 0:
                    if (self.lang == 'en' and token == u"'" and i > 0 
                        and re.match(r'[s]$', tokens[i-1]) ):
                        # Left shift on single quote for possessives ending
                        # in "s", e.g. "The Jones' house" 
                        detokenized_text += token
                        prepend_space = " "
                    else:
                        # Right shift.
                        detokenized_text += prepend_space + token
                        prepend_space = ""
                        quote_counts[normalized_quo] += 1
                else:
                    # Left shift.
                    text += token
                    prepend_space = " "
                    quote_counts[normalized_quo] += 1
            
            elif (self.lang == 'fi' and re.match(r':$', tokens[i-1])
                  and re.match(self.FINNISH_REGEX, token)):
                # Finnish : without intervening space if followed by case suffix
                # EU:N EU:n EU:ssa EU:sta EU:hun EU:iin ...
                detokenized_text += prepend_space + token
                prepend_space = " "
            
            else:
                detokenized_text += prepend_space + token
                prepend_space = " "
                
        # Merge multiple spaces.
        regexp, subsitution = self.ONE_SPACE
        detokenized_text = re.sub(regexp, subsitution, detokenized_text)
        # Removes heading and trailing spaces.
        detokenized_text = detokenized_text.strip()
    
        return detokenized_text if return_str else detokenized_text.split()