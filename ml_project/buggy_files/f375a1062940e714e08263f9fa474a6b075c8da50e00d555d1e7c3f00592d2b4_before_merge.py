def upgrade():
    try:
        op.drop_column('users', 'auth_state')
    except sa.exc.OperationalError as e:
        # sqlite3 can't drop columns
        warnings.warn("Failed to drop column: %s" % e)
    op.add_column('users', sa.Column('encrypted_auth_state', sa.types.LargeBinary))