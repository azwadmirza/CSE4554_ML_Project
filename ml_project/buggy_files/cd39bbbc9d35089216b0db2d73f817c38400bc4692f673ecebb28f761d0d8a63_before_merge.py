def downgrade():
    with op.batch_alter_table("sensor") as batch_op:
        batch_op.drop_column('cmd_command')
        batch_op.drop_column('cmd_measurement')
        batch_op.drop_column('cmd_measurement_units')