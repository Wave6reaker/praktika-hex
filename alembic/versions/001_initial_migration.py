"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2023-05-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Создание таблицы пользователей
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('role', sa.Enum('USER', 'ADMIN', name='userrole'), nullable=False, server_default='USER'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Создание таблицы комнат
    op.create_table('rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('price_per_hour', sa.Float(), nullable=False),
        sa.Column('has_projector', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('has_whiteboard', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('has_video_conf', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rooms_id'), 'rooms', ['id'], unique=False)
    op.create_index(op.f('ix_rooms_name'), 'rooms', ['name'], unique=False)
    
    # Создание таблицы бронирований
    op.create_table('bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('status', sa.Enum('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED', name='bookingstatus'), nullable=False, server_default='PENDING'),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)


def downgrade():
    # Удаление таблиц в обратном порядке
    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_table('bookings')
    
    op.drop_index(op.f('ix_rooms_name'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_id'), table_name='rooms')
    op.drop_table('rooms')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    
    # Удаление перечислений
    op.execute('DROP TYPE bookingstatus')
    op.execute('DROP TYPE userrole')