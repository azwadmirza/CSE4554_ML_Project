def assign_virtualchassis_master(instance, created, **kwargs):
    """
    When a VirtualChassis is created, automatically assign its master device to the VC.
    """
    if created:
        Device.objects.filter(pk=instance.master.pk).update(virtual_chassis=instance, vc_position=1)