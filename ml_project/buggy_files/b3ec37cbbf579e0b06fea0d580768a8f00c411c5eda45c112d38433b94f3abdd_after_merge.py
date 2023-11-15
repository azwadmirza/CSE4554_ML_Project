    def _kde_data(self, el, key, **kwargs):
        vdim = el.vdims[0]
        values = el.dimension_values(vdim)
        if self.clip:
            vdim = vdim(range=self.clip)
            el = el.clone(vdims=[vdim])
        kde = univariate_kde(el, dimension=vdim, **kwargs)
        xs, ys = (kde.dimension_values(i) for i in range(2))
        mask = isfinite(ys) & (ys>0) # Mask out non-finite and zero values
        xs, ys = xs[mask], ys[mask]
        ys = (ys/ys.max())*(self.violin_width/2.) if len(ys) else []
        ys = [key+(sign*y,) for sign, vs in ((-1, ys), (1, ys[::-1])) for y in vs]
        xs = np.concatenate([xs, xs[::-1]])
        kde =  {'ys': xs, 'xs': ys}

        bars, segments, scatter = defaultdict(list), defaultdict(list), {}
        values = el.dimension_values(vdim)
        values = values[isfinite(values)]
        if not len(values):
            pass
        elif self.inner == 'quartiles':
            for stat_fn in self._stat_fns:
                stat = stat_fn(values)
                if len(xs):
                    sidx = np.argmin(np.abs(xs-stat))
                    sx, sy = xs[sidx], ys[sidx]
                else:
                    continue
                segments['x'].append(sx)
                segments['y0'].append(key+(-sy[-1],))
                segments['y1'].append(sy)
        elif self.inner == 'stick':
            for value in values:
                sidx = np.argmin(np.abs(xs-value))
                sx, sy = xs[sidx], ys[sidx]
                segments['x'].append(sx)
                segments['y0'].append(key+(-sy[-1],))
                segments['y1'].append(sy)
        elif self.inner == 'box':
            xpos = key+(0,)
            q1, q2, q3 = (np.percentile(values, q=q)
                          for q in range(25, 100, 25))
            iqr = q3 - q1
            upper = min(q3 + 1.5*iqr, np.nanmax(values))
            lower = max(q1 - 1.5*iqr, np.nanmin(values))
            segments['x'].append(xpos)
            segments['y0'].append(lower)
            segments['y1'].append(upper)
            bars['x'].append(xpos)
            bars['bottom'].append(q1)
            bars['top'].append(q3)
            scatter['x'] = xpos
            scatter['y'] = q2
        return kde, segments, bars, scatter