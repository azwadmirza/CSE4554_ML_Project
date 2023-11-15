def upgrade():
    # proxy/table info is no longer in the database
    op.drop_table('proxies')
    op.drop_table('hubs')

    # drop some columns no longer in use
    try:
        op.drop_column('users', 'auth_state')
        op.drop_column('users', '_server_id')
    except sa.exc.OperationalError:
        # this won't be a problem moving forward, but downgrade will fail
        if op.get_context().dialect.name == 'sqlite':
            logger.warning("sqlite cannot drop columns. Leaving unused old columns in place.")
        else:
            raise

    op.add_column('users', sa.Column('encrypted_auth_state', sa.types.LargeBinary))