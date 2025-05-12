from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None
# Совпадает с типом, уже существующим в БД
userrole = ENUM('ADMIN', 'USER', name='userrole', create_type=False)

# Определим таблицу users
users = table(
    'users',
    column('email', sa.String),
    column('username', sa.String),
    column('hashed_password', sa.String),
    column('full_name', sa.String),
    column('role', userrole),
    column('is_active', sa.Boolean),
)

def upgrade():
    op.bulk_insert(users, [
        {
            'email': 'admin@example.com',
            'username': 'admin',
            'hashed_password': '$2b$12$KpWXtTudxxp.plX9ZU0Iw.P/WjCJaPvwk/DnDyT77wbCfb.LgS3vm',
            'full_name': 'Administrator',
            'role': 'ADMIN',
            'is_active': True
        }
    ])

def downgrade():
    op.execute("DELETE FROM users WHERE username = 'admin'")
