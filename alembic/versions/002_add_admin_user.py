"""Add admin user

Revision ID: 002
Revises: 001
Create Date: 2023-05-10 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Enum, Boolean
import os
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    """Создает хеш пароля"""
    return pwd_context.hash(password)

def upgrade():
    # Получаем данные администратора из переменных окружения или используем значения по умолчанию
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin")
    admin_full_name = os.getenv("ADMIN_FULL_NAME", "Administrator")
    
    # Хешируем пароль
    hashed_password = get_password_hash(admin_password)
    
    # Создаем таблицу для вставки данных
    users = table('users',
        column('id', Integer),
        column('email', String),
        column('username', String),
        column('hashed_password', String),
        column('full_name', String),
        column('role', Enum),
        column('is_active', Boolean)
    )
    
    # Вставляем администратора
    op.bulk_insert(users,
        [
            {
                'email': admin_email,
                'username': admin_username,
                'hashed_password': hashed_password,
                'full_name': admin_full_name,
                'role': 'ADMIN',
                'is_active': True
            }
        ]
    )


def downgrade():
    # Удаляем администратора
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    
    op.execute(f"DELETE FROM users WHERE username = '{admin_username}'")