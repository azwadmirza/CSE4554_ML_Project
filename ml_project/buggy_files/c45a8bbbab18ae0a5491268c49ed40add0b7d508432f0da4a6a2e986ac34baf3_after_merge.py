    def _complement(self, other):
        # this behaves as other - self
        if isinstance(other, ProductSet):
            # For each set consider it or it's complement
            # We need at least one of the sets to be complemented
            # Consider all 2^n combinations.
            # We can conveniently represent these options easily using a ProductSet

            # XXX: this doesn't work if the dimentions of the sets isn't same.
            # A - B is essentially same as A if B has a different
            # dimentionality than A
            switch_sets = ProductSet(FiniteSet(o, o - s) for s, o in
                                     zip(self.sets, other.sets))
            product_sets = (ProductSet(*set) for set in switch_sets)
            # Union of all combinations but this one
            return Union(p for p in product_sets if p != other)

        elif isinstance(other, Interval):
            if isinstance(self, Interval) or isinstance(self, FiniteSet):
                return Intersection(other, self.complement(S.Reals))

        elif isinstance(other, Union):
            return Union(o - self for o in other.args)

        elif isinstance(other, Complement):
            return Complement(other.args[0], Union(other.args[1], self))

        elif isinstance(other, EmptySet):
            return S.EmptySet

        elif isinstance(other, FiniteSet):
            return FiniteSet(*[el for el in other if self.contains(el) != True])