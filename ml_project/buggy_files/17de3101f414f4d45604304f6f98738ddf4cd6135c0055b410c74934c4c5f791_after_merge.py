def parse_inventory_id(data):
    inventory_id = data.get('inventory_id', ['null'])
    try:
        inventory_id = int(inventory_id[0])
    except ValueError:
        inventory_id = None
    except IndexError:
        inventory_id = None
    except TypeError:
        inventory_id = None
    if not inventory_id:
        inventory_id = None
    return inventory_id