    def postprocess_data(self, data):
        # Convert section names.
        for sect in data.keys():
            if sect in _SECT_CONV:
                data[_SECT_CONV[sect]] = data[sect]
                del data[sect]
                sect = _SECT_CONV[sect]
        # Filter out fake values.
        for key in data:
            value = data[key]
            if isinstance(value, list) and value:
                if isinstance(value[0], Person):
                    data[key] = filter(lambda x: x.personID is not None, value)
                if isinstance(value[0], _Container):
                    for obj in data[key]:
                        obj.accessSystem = self._as
                        obj.modFunct = self._modFunct
        if 'akas' in data or 'other akas' in data:
            akas = data.get('akas') or []
            other_akas = data.get('other akas') or []
            akas += other_akas
            nakas = []
            for aka in akas:
                aka = aka.strip()
                if aka.endswith('" -'):
                    aka = aka[:-3].rstrip()
                nakas.append(aka)
            if 'akas' in data:
                del data['akas']
            if 'other akas' in data:
                del data['other akas']
            if nakas:
                data['akas'] = nakas
        if 'runtimes' in data:
            data['runtimes'] = [x.replace(' min', u'')
                                for x in data['runtimes']]
        if 'original air date' in data:
            oid = self.re_space.sub(' ', data['original air date']).strip()
            data['original air date'] = oid
            aid = self.re_airdate.findall(oid)
            if aid and len(aid[0]) == 3:
                date, season, episode = aid[0]
                date = date.strip()
                try: season = int(season)
                except: pass
                try: episode = int(episode)
                except: pass
                if date and date != '????':
                    data['original air date'] = date
                else:
                    del data['original air date']
                # Handle also "episode 0".
                if season or type(season) is type(0):
                    data['season'] = season
                if episode or type(season) is type(0):
                    data['episode'] = episode
        for k in ('writer', 'director'):
            t_k = 'thin %s' % k
            if t_k not in data:
                continue
            if k not in data:
                data[k] = data[t_k]
            del data[t_k]
        if 'top/bottom rank' in data:
            tbVal = data['top/bottom rank'].lower()
            if tbVal.startswith('top'):
                tbKey = 'top 250 rank'
                tbVal = _toInt(tbVal, [('top 250: #', '')])
            else:
                tbKey = 'bottom 100 rank'
                tbVal = _toInt(tbVal, [('bottom 100: #', '')])
            if tbVal:
                data[tbKey] = tbVal
            del data['top/bottom rank']
        if 'year' in data and data['year'] == '????':
            del data['year']
        if 'tv series link' in data:
            if 'tv series title' in data:
                data['episode of'] = Movie(title=data['tv series title'],
                                            movieID=analyze_imdbid(
                                                    data['tv series link']),
                                            accessSystem=self._as,
                                            modFunct=self._modFunct)
                del data['tv series title']
            del data['tv series link']
        if 'rating' in data:
            try:
                data['rating'] = float(data['rating'].replace('/10', ''))
            except (TypeError, ValueError):
                pass
        if 'votes' in data:
            try:
                votes = data['votes'].replace(',', '').replace('votes', '')
                data['votes'] = int(votes)
            except (TypeError, ValueError):
                pass
        return data