def create_allocations(apps, schema_editor):
    Allocation = apps.get_model("warehouse", "Allocation")
    OrderLine = apps.get_model("order", "OrderLine")
    Warehouse = apps.get_model("warehouse", "Warehouse")
    for warehouse in Warehouse.objects.iterator():
        shipping_zone_pk = warehouse.shipping_zones.first().pk
        for order_line in OrderLine.objects.filter(
            order__shipping_method__shipping_zone__pk=shipping_zone_pk,
        ).iterator():
            quantity_unfulfilled = order_line.quantity - order_line.quantity_fulfilled
            if quantity_unfulfilled > 0 and order_line.variant:
                create_allocation(
                    order_line.variant,
                    warehouse,
                    order_line,
                    quantity_unfulfilled,
                    Allocation,
                )