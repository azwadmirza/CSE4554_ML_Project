def post_delete_linked(sender, instance, **kwargs):
    # When removing project, the linked component might be already deleted now
    try:
        if instance.linked_component:
            instance.linked_component.update_alerts()
    except Component.DoesNotExist:
        pass