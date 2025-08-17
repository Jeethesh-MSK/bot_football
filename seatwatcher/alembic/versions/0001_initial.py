from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
	op.create_table(
		'observations',
		sa.Column('id', sa.Integer(), nullable=False),
		sa.Column('created_at', sa.DateTime(), nullable=False),
		sa.Column('match_id', sa.String(length=256), nullable=False),
		sa.Column('seats_available', sa.Integer(), nullable=False),
		sa.PrimaryKeyConstraint('id')
	)
	op.create_index(op.f('ix_observations_match_id'), 'observations', ['match_id'], unique=False)

	op.create_table(
		'notification_logs',
		sa.Column('id', sa.Integer(), nullable=False),
		sa.Column('created_at', sa.DateTime(), nullable=False),
		sa.Column('match_id', sa.String(length=256), nullable=False),
		sa.Column('channel', sa.String(length=64), nullable=False),
		sa.Column('subject', sa.String(length=512), nullable=False),
		sa.Column('message', sa.Text(), nullable=True),
		sa.Column('seats_available', sa.Integer(), nullable=True),
		sa.PrimaryKeyConstraint('id')
	)
	op.create_index(op.f('ix_notification_logs_match_id'), 'notification_logs', ['match_id'], unique=False)
	op.create_index(op.f('ix_notification_logs_channel'), 'notification_logs', ['channel'], unique=False)
	op.create_unique_constraint('uq_notif_time_match_channel', 'notification_logs', ['created_at', 'match_id', 'channel'])


def downgrade() -> None:
	op.drop_constraint('uq_notif_time_match_channel', 'notification_logs', type_='unique')
	op.drop_index(op.f('ix_notification_logs_channel'), table_name='notification_logs')
	op.drop_index(op.f('ix_notification_logs_match_id'), table_name='notification_logs')
	op.drop_table('notification_logs')

	op.drop_index(op.f('ix_observations_match_id'), table_name='observations')
	op.drop_table('observations')