def downgrade():
    op.drop_column('users', 'encrypted_auth_state')
    op.add_column('users', sa.Column('auth_state', JSONDict))