# backend/alembic/versions/001_chatbot_enhancements.py
"""chatbot enhancements

Revision ID: 001_chatbot_enhancements
Revises: 
Create Date: 2024-09-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_chatbot_enhancements'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create crew_certification table
    op.create_table('crew_certification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('crew_id', sa.Integer(), nullable=False),
        sa.Column('cert_type', sa.String(length=100), nullable=False),
        sa.Column('aircraft_type', sa.String(length=50), nullable=True),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['crew_id'], ['crew.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crew_certification_crew_id'), 'crew_certification', ['crew_id'], unique=False)
    op.create_index(op.f('ix_crew_certification_expiry_date'), 'crew_certification', ['expiry_date'], unique=False)

    # Create crew_training table
    op.create_table('crew_training',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('crew_id', sa.Integer(), nullable=False),
        sa.Column('course', sa.String(length=200), nullable=False),
        sa.Column('valid_from', sa.Date(), nullable=False),
        sa.Column('valid_to', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='active', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['crew_id'], ['crew.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crew_training_valid_to'), 'crew_training', ['valid_to'], unique=False)

    # Create pairing table
    op.create_table('pairing',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pairing_code', sa.String(length=20), nullable=False),
        sa.Column('origin', sa.String(length=3), nullable=False),
        sa.Column('destination', sa.String(length=3), nullable=False),
        sa.Column('sectors', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('planned_start', sa.DateTime(), nullable=False),
        sa.Column('planned_end', sa.DateTime(), nullable=False),
        sa.Column('aircraft_type', sa.String(length=50), nullable=False),
        sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('pairing_code')
    )
    op.create_index(op.f('ix_pairing_planned_start_planned_end'), 'pairing', ['planned_start', 'planned_end'], unique=False)

    # Create leave_request table
    op.create_table('leave_request',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('crew_id', sa.Integer(), nullable=False),
        sa.Column('leave_start', sa.DateTime(), nullable=False),
        sa.Column('leave_end', sa.DateTime(), nullable=False),
        sa.Column('leave_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='pending', nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['crew_id'], ['crew.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leave_request_leave_start_leave_end'), 'leave_request', ['leave_start', 'leave_end'], unique=False)

    # Create weather_forecast table
    op.create_table('weather_forecast',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('airport_code', sa.String(length=3), nullable=False),
        sa.Column('forecast_time', sa.DateTime(), nullable=False),
        sa.Column('valid_from', sa.DateTime(), nullable=False),
        sa.Column('valid_to', sa.DateTime(), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_weather_forecast_airport_code_valid_from'), 'weather_forecast', ['airport_code', 'valid_from'], unique=False)

    # Create disruption_event table
    op.create_table('disruption_event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('affected_pairings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create credential_audit_log table
    op.create_table('credential_audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('crew_id', sa.Integer(), nullable=False),
        sa.Column('snapshot_time', sa.DateTime(), nullable=False),
        sa.Column('active_certificates', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['crew_id'], ['crew.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('credential_audit_log')
    op.drop_table('disruption_event')
    op.drop_table('weather_forecast')
    op.drop_table('leave_request')
    op.drop_table('pairing')
    op.drop_table('crew_training')
    op.drop_table('crew_certification')