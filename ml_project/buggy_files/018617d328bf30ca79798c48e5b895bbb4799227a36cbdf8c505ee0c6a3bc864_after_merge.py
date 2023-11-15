    def _intersect(self, other):
        from sympy.functions.elementary.integers import ceiling, floor
        from sympy.functions.elementary.complexes import sign

        if other is S.Naturals:
            return self._intersect(Interval(1, S.Infinity))

        if other is S.Integers:
            return self

        if other.is_Interval:
            if not all(i.is_number for i in other.args[:2]):
                return

            # trim down to self's size, and represent
            # as a Range with step 1
            start = ceiling(max(other.inf, self.inf))
            if start not in other:
                start += 1
            end = floor(min(other.sup, self.sup))
            if end not in other:
                end -= 1
            return self.intersect(Range(start, end + 1))

        if isinstance(other, Range):
            from sympy.solvers.diophantine import diop_linear
            from sympy.core.numbers import ilcm

            # non-overlap quick exits
            if not other:
                return S.EmptySet
            if not self:
                return S.EmptySet
            if other.sup < self.inf:
                return S.EmptySet
            if other.inf > self.sup:
                return S.EmptySet

            # work with finite end at the start
            r1 = self
            if r1.start.is_infinite:
                r1 = r1.reversed
            r2 = other
            if r2.start.is_infinite:
                r2 = r2.reversed

            # this equation represents the values of the Range;
            # it's a linear equation
            eq = lambda r, i: r.start + i*r.step

            # we want to know when the two equations might
            # have integer solutions so we use the diophantine
            # solver
            a, b = diop_linear(eq(r1, Dummy()) - eq(r2, Dummy()))

            # check for no solution
            no_solution = a is None and b is None
            if no_solution:
                return S.EmptySet

            # there is a solution
            # -------------------

            # find the coincident point, c
            a0 = a.as_coeff_Add()[0]
            c = eq(r1, a0)

            # find the first point, if possible, in each range
            # since c may not be that point
            def _first_finite_point(r1, c):
                if c == r1.start:
                    return c
                # st is the signed step we need to take to
                # get from c to r1.start
                st = sign(r1.start - c)*step
                # use Range to calculate the first point:
                # we want to get as close as possible to
                # r1.start; the Range will not be null since
                # it will at least contain c
                s1 = Range(c, r1.start + st, st)[-1]
                if s1 == r1.start:
                    pass
                else:
                    # if we didn't hit r1.start then, if the
                    # sign of st didn't match the sign of r1.step
                    # we are off by one and s1 is not in r1
                    if sign(r1.step) != sign(st):
                        s1 -= st
                if s1 not in r1:
                    return
                return s1

            # calculate the step size of the new Range
            step = abs(ilcm(r1.step, r2.step))
            s1 = _first_finite_point(r1, c)
            if s1 is None:
                return S.EmptySet
            s2 = _first_finite_point(r2, c)
            if s2 is None:
                return S.EmptySet

            # replace the corresponding start or stop in
            # the original Ranges with these points; the
            # result must have at least one point since
            # we know that s1 and s2 are in the Ranges
            def _updated_range(r, first):
                st = sign(r.step)*step
                if r.start.is_finite:
                    rv = Range(first, r.stop, st)
                else:
                    rv = Range(r.start, first + st, st)
                return rv
            r1 = _updated_range(self, s1)
            r2 = _updated_range(other, s2)

            # work with them both in the increasing direction
            if sign(r1.step) < 0:
                r1 = r1.reversed
            if sign(r2.step) < 0:
                r2 = r2.reversed

            # return clipped Range with positive step; it
            # can't be empty at this point
            start = max(r1.start, r2.start)
            stop = min(r1.stop, r2.stop)
            return Range(start, stop, step)
        else:
            return