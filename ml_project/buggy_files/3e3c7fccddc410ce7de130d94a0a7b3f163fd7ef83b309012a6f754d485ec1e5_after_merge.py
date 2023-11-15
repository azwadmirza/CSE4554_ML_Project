def check_status(monster, status_name):
    return any(t for t in monster.status if t.slug == status_name)