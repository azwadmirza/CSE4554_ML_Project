def downgrade():
    # drop all the new tables
    engine = op.get_bind().engine
    for table in ('oauth_clients',
                  'oauth_codes',
                  'oauth_access_tokens',
                  'spawners'):
        if engine.has_table(table):
            op.drop_table(table)

    op.drop_column('users', 'encrypted_auth_state')

    op.add_column('users', sa.Column('auth_state', JSONDict))
    op.add_column('users',  sa.Column('_server_id', sa.Integer, sa.ForeignKey('servers.id')))