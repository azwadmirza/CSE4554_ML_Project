def get_or_create_warehouse(apps):
    Warehouse = apps.get_model("warehouse", "Warehouse")
    ShippingZone = apps.get_model("shipping", "ShippingZone")
    Site = apps.get_model("sites", "Site")

    warehouses = Warehouse.objects.annotate(
        zones_count=models.Count("shipping_zones")
    ).filter(zones_count=ShippingZone.objects.count())
    if warehouses.first() is not None:
        return warehouses.first()

    site_settings = Site.objects.get_current().settings
    address = getattr(site_settings, "company_address", None)
    if address is None:
        Address = apps.get_model("account", "Address")
        address = Address.objects.create()

    warehouse = Warehouse.objects.create(name="Default warehouse", address=address)
    warehouse.shipping_zones.add(*ShippingZone.objects.all())
    return warehouse