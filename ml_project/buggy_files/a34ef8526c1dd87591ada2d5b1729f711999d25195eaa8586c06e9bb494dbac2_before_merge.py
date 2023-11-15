    def __init__(self, lst):
        """
        Input to this constructor can be one of a few things:

        1. A list of one UnifiedResponse object
        2. A list of tuples (QueryResponse, client)
        """

        tmplst = []
        # numfile is the number of files not the number of results.
        self._numfile = 0
        if isinstance(lst, QueryResponse):
            if not hasattr(lst, 'client'):
                raise("QueryResponse is only a valid input if it has a client attribute.")
            tmplst.append(lst)
            self._numfile = len(lst)
        else:
            for block in lst:
                if isinstance(block, tuple) and len(block) == 2:
                    block[0].client = block[1]
                    tmplst.append(block[0])
                    self._numfile += len(block[0])
                elif hasattr(block, 'client'):
                    tmplst.append(block)
                    self._numfile += len(block)
                else:
                    raise Exception("{} is not a valid input to UnifiedResponse.".format(type(lst)))

        self._list = tmplst