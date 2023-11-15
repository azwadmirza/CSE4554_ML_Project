    def calculateWhatChecker(self, length_text, key):
        """Calculates what threshold / checker to use

        If the length of the text is over the maximum sentence length, use the last checker / threshold
        Otherwise, traverse the keys backwards until we find a key range that does not fit.
        So we traverse backwards and see if the sentence length is between current - 1 and current
        In this way, we find the absolute lowest checker / percentage threshold. 
        We traverse backwards because if the text is longer than the max sentence length, we already know.
        In total, the keys are only 5 items long or so. It is not expensive to move backwards, nor is it expensive to move forwards.

        Args:
            length_text -> The length of the text
            key -> What key we want to use. I.E. Phase1 keys, Phase2 keys.
        Returns:
            what_to_use -> the key of the lowest checker."""

        _keys = list(key)
        _keys = list(map(int, _keys))
        if length_text >= int(_keys[-1]):
            what_to_use = list(key)[_keys.index(_keys[-1])]
        else:
            # this algorithm finds the smallest possible fit for the text
            for counter, i in reversed(list(enumerate(_keys))):
                #  [0, 110, 150]
                if i <= length_text:
                    what_to_use = i
        return what_to_use