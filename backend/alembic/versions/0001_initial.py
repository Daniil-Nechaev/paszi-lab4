"""initial tables: users, resources, resource_permissions
Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('login', sa.String(length=32), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_login', 'users', ['login'], unique=True)

    op.create_table('resources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('expires_at', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_resources_owner_id', 'resources', ['owner_id'])

    op.create_table('resource_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('can_read', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('can_update', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('can_delete', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.ForeignKeyConstraint(['resource_id'], ['resources.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('resource_id', 'user_id', name='uq_resource_user')
    )
    op.create_index('ix_resource_permissions_resource_id', 'resource_permissions', ['resource_id'])
    op.create_index('ix_resource_permissions_user_id', 'resource_permissions', ['user_id'])

def downgrade() -> None:
    op.drop_index('ix_resource_permissions_user_id', table_name='resource_permissions')
    op.drop_index('ix_resource_permissions_resource_id', table_name='resource_permissions')
    op.drop_table('resource_permissions')
    op.drop_index('ix_resources_owner_id', table_name='resources')
    op.drop_table('resources')
    op.drop_index('ix_users_login', table_name='users')
    op.drop_table('users')