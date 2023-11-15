def assign_virtualchassis_master(instance, created, **kwargs):
    """
    When a VirtualChassis is created, automatically assign its master device to the VC.
    """
    # Default to 1 but don't overwrite an existing position (see #2087)
    if instance.master.vc_position is not None:
        vc_position = instance.master.vc_position
    else:
        vc_position = 1
    if created:
        Device.objects.filter(pk=instance.master.pk).update(virtual_chassis=instance, vc_position=vc_position)