    def subdiagram_from_objects(self, objects):
        """
        If ``objects`` is a subset of the objects of ``self``, returns
        a diagram which has as premises all those premises of ``self``
        which have a domains and codomains in ``objects``, likewise
        for conclusions.  Properties are preserved.

        Examples
        ========

        >>> from sympy.categories import Object, NamedMorphism, Diagram
        >>> from sympy import FiniteSet
        >>> A = Object("A")
        >>> B = Object("B")
        >>> C = Object("C")
        >>> f = NamedMorphism(A, B, "f")
        >>> g = NamedMorphism(B, C, "g")
        >>> d = Diagram([f, g], {f: "unique", g*f: "veryunique"})
        >>> d1 = d.subdiagram_from_objects(FiniteSet(A, B))
        >>> d1 == Diagram([f], {f: "unique"})
        True
        """
        if not objects.is_subset(self.objects):
            raise ValueError(
                "Supplied objects should all belong to the diagram.")

        new_premises = {}
        for morphism, props in self.premises.items():
            if (morphism.domain in objects) and (morphism.codomain in objects):
                new_premises[morphism] = props

        new_conclusions = {}
        for morphism, props in self.conclusions.items():
            if (morphism.domain in objects) and (morphism.codomain in objects):
                new_conclusions[morphism] = props

        return Diagram(new_premises, new_conclusions)