    def __init__(self, pos, name, bases, doc, body, decorators=None,
                 keyword_args=None, force_py3_semantics=False):
        StatNode.__init__(self, pos)
        self.name = name
        self.doc = doc
        self.body = body
        self.decorators = decorators
        self.bases = bases
        from . import ExprNodes
        if self.doc and Options.docstrings:
            doc = embed_position(self.pos, self.doc)
            doc_node = ExprNodes.StringNode(pos, value=doc)
        else:
            doc_node = None

        allow_py2_metaclass = not force_py3_semantics
        if keyword_args:
            allow_py2_metaclass = False
            self.is_py3_style_class = True
            if keyword_args.is_dict_literal:
                if keyword_args.key_value_pairs:
                    for i, item in list(enumerate(keyword_args.key_value_pairs))[::-1]:
                        if item.key.value == 'metaclass':
                            if self.metaclass is not None:
                                error(item.pos, "keyword argument 'metaclass' passed multiple times")
                            # special case: we already know the metaclass,
                            # so we don't need to do the "build kwargs,
                            # find metaclass" dance at runtime
                            self.metaclass = item.value
                            del keyword_args.key_value_pairs[i]
                    self.mkw = keyword_args
                else:
                    assert self.metaclass is not None
            else:
                # MergedDictNode
                self.mkw = ExprNodes.ProxyNode(keyword_args)

        if force_py3_semantics or self.bases or self.mkw or self.metaclass:
            if self.metaclass is None:
                if keyword_args and not keyword_args.is_dict_literal:
                    # **kwargs may contain 'metaclass' arg
                    mkdict = self.mkw
                else:
                    mkdict = None
                if (not mkdict and
                        self.bases.is_sequence_constructor and
                        not self.bases.args):
                    pass  # no base classes => no inherited metaclass
                else:
                    self.metaclass = ExprNodes.PyClassMetaclassNode(
                        pos, class_def_node=self)
                needs_metaclass_calculation = False
            else:
                needs_metaclass_calculation = True

            self.dict = ExprNodes.PyClassNamespaceNode(
                pos, name=name, doc=doc_node, class_def_node=self)
            self.classobj = ExprNodes.Py3ClassNode(
                pos, name=name, class_def_node=self, doc=doc_node,
                calculate_metaclass=needs_metaclass_calculation,
                allow_py2_metaclass=allow_py2_metaclass)
        else:
            # no bases, no metaclass => old style class creation
            self.dict = ExprNodes.DictNode(pos, key_value_pairs=[])
            self.classobj = ExprNodes.ClassNode(
                pos, name=name, class_def_node=self, doc=doc_node)

        self.target = ExprNodes.NameNode(pos, name=name)
        self.class_cell = ExprNodes.ClassCellInjectorNode(self.pos)