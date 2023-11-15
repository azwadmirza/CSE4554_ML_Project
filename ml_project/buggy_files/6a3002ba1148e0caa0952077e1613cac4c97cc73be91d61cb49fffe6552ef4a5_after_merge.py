def is_model_subclass_info(info: TypeInfo, django_context: 'DjangoContext') -> bool:
    return (info.fullname() in django_context.all_registered_model_class_fullnames
            or info.has_base(fullnames.MODEL_CLASS_FULLNAME))