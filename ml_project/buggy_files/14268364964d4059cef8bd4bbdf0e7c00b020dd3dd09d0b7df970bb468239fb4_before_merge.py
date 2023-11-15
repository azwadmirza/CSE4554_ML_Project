    def __new__(cls, *args, **kwargs):
        instance = super(OutputOptionsWithTextMixIn, cls).__new__(
            cls, *args, **kwargs
        )
        utils.warn_until(
            (0, 19),
            '\'OutputOptionsWithTextMixIn\' has been deprecated. Please '
            'start using \'OutputOptionsMixIn\'; your code should not need '
            'any further changes.'
        )
        return instance