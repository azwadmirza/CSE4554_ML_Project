                def patch() -> None:
                    self.perform_transform(node,
                        lambda tp: tp.accept(ForwardReferenceResolver(self.fail,
                                                                      node, warn)))