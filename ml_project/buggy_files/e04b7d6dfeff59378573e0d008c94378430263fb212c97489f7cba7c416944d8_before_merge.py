    def postprocess_data(self, data):
        if not data or self.label not in data:
            return []
        mlist = []
        data = data[self.label]
        # Avoid duplicates.  A real fix, using XPath, is auspicabile.
        # XXX: probably this is no more needed.
        seenIDs = []
        for d in data:
            if 'movieID' not in d: continue
            if self.ranktext not in d: continue
            if 'title' not in d: continue
            theID = analyze_imdbid(d['movieID'])
            if theID is None:
                continue
            theID = str(theID)
            if theID in seenIDs:
                continue
            seenIDs.append(theID)
            minfo = analyze_title(d['title'])
            try: minfo[self.ranktext] = int(d[self.ranktext].replace('.', ''))
            except: pass
            if 'votes' in d:
                try: minfo['votes'] = int(d['votes'].replace(',', ''))
                except: pass
            if 'rating' in d:
                try: minfo['rating'] = float(d['rating'])
                except: pass
            mlist.append((theID, minfo))
        return mlist