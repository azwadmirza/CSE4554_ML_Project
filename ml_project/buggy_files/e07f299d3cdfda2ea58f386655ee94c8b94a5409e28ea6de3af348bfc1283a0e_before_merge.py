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
        op.drop_constraint('known_event_user_id_fkey', 'known_event')

    if "chart" in tables:
        op.drop_table(
            "chart",
        )

    if "users" in tables:
        op.drop_table("users")