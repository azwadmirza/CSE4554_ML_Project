    def __init__(self, text: str = None, use_tokenizer: bool = False, labels: List[Label] = None):

        super(Sentence, self).__init__()

        self.tokens: List[Token] = []

        self.labels: List[Label] = labels

        self._embeddings: Dict = {}

        # if text is passed, instantiate sentence with tokens (words)
        if text is not None:

            # tokenize the text first if option selected
            if use_tokenizer:

                # use segtok for tokenization
                tokens = []
                sentences = split_single(text)
                for sentence in sentences:
                    contractions = split_contractions(word_tokenizer(sentence))
                    tokens.extend(contractions)

                # determine offsets for whitespace_after field
                index = text.index
                running_offset = 0
                last_word_offset = -1
                last_token = None
                for word in tokens:
                    token = Token(word)
                    self.add_token(token)
                    try:
                        word_offset = index(word, running_offset)
                    except:
                        word_offset = last_word_offset + 1
                    if word_offset - 1 == last_word_offset and last_token is not None:
                        last_token.whitespace_after = False
                    word_len = len(word)
                    running_offset = word_offset + word_len
                    last_word_offset = running_offset - 1
                    last_token = token

            # otherwise assumes whitespace tokenized text
            else:
                # add each word in tokenized string as Token object to Sentence
                for word in text.split(' '):
                    token = Token(word)
                    self.add_token(token)