    def __call__(self, *sequences):
        client = self.view.client
        
        # check that the length of sequences match
        len_0 = len(sequences[0])
        for s in sequences:
            if len(s)!=len_0:
                msg = 'all sequences must have equal length, but %i!=%i'%(len_0,len(s))
                raise ValueError(msg)
        balanced = 'Balanced' in self.view.__class__.__name__
        if balanced:
            if self.chunksize:
                nparts = len_0//self.chunksize + int(len_0%self.chunksize > 0)
            else:
                nparts = len_0
            targets = [None]*nparts
        else:
            if self.chunksize:
                warnings.warn("`chunksize` is ignored unless load balancing", UserWarning)
            # multiplexed:
            targets = self.view.targets
            # 'all' is lazily evaluated at execution time, which is now:
            if targets == 'all':
                targets = client._build_targets(targets)[1]
            nparts = len(targets)

        msg_ids = []
        for index, t in enumerate(targets):
            args = []
            for seq in sequences:
                part = self.mapObject.getPartition(seq, index, nparts)
                if len(part) == 0:
                    continue
                else:
                    args.append(part)
            if not args:
                continue

            # print (args)
            if hasattr(self, '_map'):
                if sys.version_info[0] >= 3:
                    f = lambda f, *sequences: list(map(f, *sequences))
                else:
                    f = map
                args = [self.func]+args
            else:
                f=self.func

            view = self.view if balanced else client[t]
            with view.temp_flags(block=False, **self.flags):
                ar = view.apply(f, *args)

            msg_ids.append(ar.msg_ids[0])

        r = AsyncMapResult(self.view.client, msg_ids, self.mapObject, 
                            fname=self.func.__name__,
                            ordered=self.ordered
                        )

        if self.block:
            try:
                return r.get()
            except KeyboardInterrupt:
                return r
        else:
            return r