def upgrade():  # noqa: D103
    # We previously had a KnownEvent's table, but we deleted the table without
    # a down migration to remove it (so we didn't delete anyone's data if they
    # were happing to use the feature.
    #
    # But before we can delete the users table we need to drop the FK

    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'known_event' in tables:
        for fkey in inspector.get_foreign_keys(table_name="known_event", referred_table="users"):
            op.drop_constraint(fkey['name'], 'known_event', type_="foreignkey")

    if "chart" in tables:
        op.drop_table(
            "chart",
        )

    if "users" in tables:
        op.drop_table("users")