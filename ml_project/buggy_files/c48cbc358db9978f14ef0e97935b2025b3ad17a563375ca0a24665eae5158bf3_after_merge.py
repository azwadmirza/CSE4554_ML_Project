    def __new__(cls, *args):
        """
        Construct a new instance of Diagram.

        If no arguments are supplied, an empty diagram is created.

        If at least an argument is supplied, ``args[0]`` is
        interpreted as the premises of the diagram.  If ``args[0]`` is
        a list, it is interpreted as a list of :class:`Morphism`'s, in
        which each :class:`Morphism` has an empty set of properties.
        If ``args[0]`` is a Python dictionary or a :class:`Dict`, it
        is interpreted as a dictionary associating to some
        :class:`Morphism`'s some properties.

        If at least two arguments are supplied ``args[1]`` is
        interpreted as the conclusions of the diagram.  The type of
        ``args[1]`` is interpreted in exactly the same way as the type
        of ``args[0]``.  If only one argument is supplied, the diagram
        has no conclusions.

        Examples
        ========

        >>> from sympy.categories import Object, NamedMorphism
        >>> from sympy.categories import IdentityMorphism, Diagram
        >>> A = Object("A")
        >>> B = Object("B")
        >>> C = Object("C")
        >>> f = NamedMorphism(A, B, "f")
        >>> g = NamedMorphism(B, C, "g")
        >>> d = Diagram([f, g])
        >>> IdentityMorphism(A) in d.premises.keys()
        True
        >>> g * f in d.premises.keys()
        True
        >>> d = Diagram([f, g], {g * f: "unique"})
        >>> d.conclusions[g * f]
        {unique}

        """
        premises = {}
        conclusions = {}

        # Here we will keep track of the objects which appear in the
        # premises.
        objects = EmptySet()

        if len(args) >= 1:
            # We've got some premises in the arguments.
            premises_arg = args[0]

            if isinstance(premises_arg, list):
                # The user has supplied a list of morphisms, none of
                # which have any attributes.
                empty = EmptySet()

                for morphism in premises_arg:
                    objects |= FiniteSet(morphism.domain, morphism.codomain)
                    Diagram._add_morphism_closure(premises, morphism, empty)
            elif isinstance(premises_arg, dict) or isinstance(premises_arg, Dict):
                # The user has supplied a dictionary of morphisms and
                # their properties.
                for morphism, props in premises_arg.items():
                    objects |= FiniteSet(morphism.domain, morphism.codomain)
                    Diagram._add_morphism_closure(
                        premises, morphism, FiniteSet(*props) if iterable(props) else FiniteSet(props))

        if len(args) >= 2:
            # We also have some conclusions.
            conclusions_arg = args[1]

            if isinstance(conclusions_arg, list):
                # The user has supplied a list of morphisms, none of
                # which have any attributes.
                empty = EmptySet()

                for morphism in conclusions_arg:
                    # Check that no new objects appear in conclusions.
                    if ((objects.contains(morphism.domain) == S.true) and
                        (objects.contains(morphism.codomain) == S.true)):
                        # No need to add identities and recurse
                        # composites this time.
                        Diagram._add_morphism_closure(
                            conclusions, morphism, empty, add_identities=False,
                            recurse_composites=False)
            elif isinstance(conclusions_arg, dict) or \
                    isinstance(conclusions_arg, Dict):
                # The user has supplied a dictionary of morphisms and
                # their properties.
                for morphism, props in conclusions_arg.items():
                    # Check that no new objects appear in conclusions.
                    if (morphism.domain in objects) and \
                       (morphism.codomain in objects):
                        # No need to add identities and recurse
                        # composites this time.
                        Diagram._add_morphism_closure(
                            conclusions, morphism, FiniteSet(*props) if iterable(props) else FiniteSet(props),
                            add_identities=False, recurse_composites=False)

        return Basic.__new__(cls, Dict(premises), Dict(conclusions), objects)