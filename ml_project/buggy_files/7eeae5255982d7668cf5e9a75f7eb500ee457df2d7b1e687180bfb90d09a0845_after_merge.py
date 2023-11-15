def clean_text(
    freqdist: Dict[str, int],
    non_single_word: int,
    top_words: Optional[int] = 30,
    stopword: Optional[bool] = True,
    lemmatize: Optional[bool] = False,
    stem: Optional[bool] = False,
) -> Dict[Any, Any]:
    """
    clean the frequency dictionary by stopwords, lemmatization and stemming
    """  # pylint: disable=too-many-arguments
    freq_copy = copy.deepcopy(freqdist)
    lemmatizer = WordNetLemmatizer()
    porter = PorterStemmer()
    for key in freq_copy.keys():
        if stopword and non_single_word > top_words:  # type: ignore
            if key in english_stopwords.english_stopwords or len(key) <= 2:
                del freqdist[key]
        if lemmatize:
            if lemmatizer.lemmatize(key) != key:
                freqdist[lemmatizer.lemmatize(key)] = freqdist[key]
                del freqdist[key]
        if stem:
            if porter.stem(key) != key:
                freqdist[porter.stem(key)] = freqdist[key]
                del freqdist[key]
    return freqdist