    def apply(self, schema, context):
        attrsubj = context.get(AnnotationSubjectCommandContext)
        assert attrsubj, "Annotation commands must be run in " + \
                         "AnnotationSubject context"

        name = sn.shortname_from_fullname(self.classname)
        attrs = attrsubj.scls.get_annotations(schema)
        annotation = attrs.get(schema, name, None)
        if annotation is None:
            schema, annotation = super().apply(schema, context)
        else:
            schema, annotation = sd.AlterObject.apply(self, schema, context)

        return schema, annotation