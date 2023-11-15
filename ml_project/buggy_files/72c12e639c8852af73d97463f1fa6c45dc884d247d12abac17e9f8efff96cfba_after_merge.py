def upgrade(ver, session):
    if ver is None or ver <= 5:
        raise db_schema.UpgradeImpossible
    return ver