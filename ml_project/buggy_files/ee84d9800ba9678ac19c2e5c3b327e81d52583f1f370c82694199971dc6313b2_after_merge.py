def ComponentTerms(cls):
    """
    Takes a Class instance and returns a generator over the classes that
    are involved in its definition, ignoring unnamed classes
    """
    if OWL_NS.Restriction in cls.type:
        try:
            cls = CastClass(cls, Individual.factoryGraph)
            for s, p, innerClsId in cls.factoryGraph.triples_choices(
                (cls.identifier,
                 [OWL_NS.allValuesFrom,
                  OWL_NS.someValuesFrom],
                 None)):
                innerCls = Class(innerClsId, skipOWLClassMembership=True)
                if isinstance(innerClsId, BNode):
                    for _c in ComponentTerms(innerCls):
                        yield _c
                else:
                    yield innerCls
        except:
            pass
    else:
        cls = CastClass(cls, Individual.factoryGraph)
        if isinstance(cls, BooleanClass):
            for _cls in cls:
                _cls = Class(_cls, skipOWLClassMembership=True)
                if isinstance(_cls.identifier, BNode):
                    for _c in ComponentTerms(_cls):
                        yield _c
                else:
                    yield _cls
        else:
            for innerCls in cls.subClassOf:
                if isinstance(innerCls.identifier, BNode):
                    for _c in ComponentTerms(innerCls):
                        yield _c
                else:
                    yield innerCls
            for s, p, o in cls.factoryGraph.triples_choices(
                (classOrIdentifier(cls),
                 CLASS_RELATIONS,
                 None)
            ):
                if isinstance(o, BNode):
                    for _c in ComponentTerms(
                            CastClass(o, Individual.factoryGraph)):
                        yield _c
                else:
                    yield innerCls