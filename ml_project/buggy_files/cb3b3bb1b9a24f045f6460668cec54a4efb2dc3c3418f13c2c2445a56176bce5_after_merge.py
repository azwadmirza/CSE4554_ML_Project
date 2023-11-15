def upgrade():
    with op.batch_alter_table("sensor") as batch_op:
        batch_op.add_column(sa.Column('cmd_command', sa.TEXT))
        batch_op.add_column(sa.Column('cmd_measurement', sa.TEXT))
        batch_op.add_column(sa.Column('cmd_measurement_units', sa.TEXT))

    with op.batch_alter_table("pid") as batch_op:
        batch_op.drop_column('sensor_id')

    op.execute(
        '''
        UPDATE pid
        SET measurement=''
        '''
    )

    op.execute(
        '''
        UPDATE pid
        SET is_activated=0
        '''
    )