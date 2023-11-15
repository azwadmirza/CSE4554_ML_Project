    def run_with_model_cls(self, model_cls: Type[Model]) -> None:
        # add related managers
        for relation in self.django_context.get_model_relations(model_cls):
            attname = relation.get_accessor_name()
            if attname is None:
                # no reverse accessor
                continue

            related_model_cls = self.django_context.get_field_related_model_cls(relation)
            if related_model_cls is None:
                continue

            related_model_info = self.lookup_class_typeinfo_or_incomplete_defn_error(related_model_cls)
            if isinstance(relation, OneToOneRel):
                self.add_new_node_to_model_class(attname, Instance(related_model_info, []))
                continue

            if isinstance(relation, (ManyToOneRel, ManyToManyRel)):
                manager_info = self.lookup_typeinfo_or_incomplete_defn_error(fullnames.RELATED_MANAGER_CLASS_FULLNAME)
                self.add_new_node_to_model_class(attname,
                                                 Instance(manager_info, [Instance(related_model_info, [])]))
                continue