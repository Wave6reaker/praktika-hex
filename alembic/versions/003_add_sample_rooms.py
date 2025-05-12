"""Add sample rooms

Revision ID: 003
Revises: 002
Create Date: 2023-05-10 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Float, Boolean, Text

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Создаем таблицу для вставки данных
    rooms = table('rooms',
        column('id', Integer),
        column('name', String),
        column('description', Text),
        column('capacity', Integer),
        column('price_per_hour', Float),
        column('has_projector', Boolean),
        column('has_whiteboard', Boolean),
        column('has_video_conf', Boolean),
        column('is_active', Boolean),
        column('image_url', String)
    )
    
    # Вставляем примеры комнат
    op.bulk_insert(rooms,
        [
            {
                'name': 'Переговорная "Москва"',
                'description': 'Просторная переговорная комната для деловых встреч и презентаций',
                'capacity': 10,
                'price_per_hour': 1000.0,
                'has_projector': True,
                'has_whiteboard': True,
                'has_video_conf': True,
                'is_active': True,
                'image_url': 'https://example.com/images/room1.jpg'
            },
            {
                'name': 'Кабинет "Токио"',
                'description': 'Уютный кабинет для индивидуальной работы или встреч один-на-один',
                'capacity': 2,
                'price_per_hour': 500.0,
                'has_projector': False,
                'has_whiteboard': True,
                'has_video_conf': False,
                'is_active': True,
                'image_url': 'https://example.com/images/room2.jpg'
            },
            {
                'name': 'Конференц-зал "Нью-Йорк"',
                'description': 'Большой конференц-зал для проведения мероприятий и тренингов',
                'capacity': 30,
                'price_per_hour': 2000.0,
                'has_projector': True,
                'has_whiteboard': True,
                'has_video_conf': True,
                'is_active': True,
                'image_url': 'https://example.com/images/room3.jpg'
            },
            {
                'name': 'Рабочая зона "Берлин"',
                'description': 'Открытая рабочая зона с несколькими столами для командной работы',
                'capacity': 8,
                'price_per_hour': 800.0,
                'has_projector': False,
                'has_whiteboard': True,
                'has_video_conf': False,
                'is_active': True,
                'image_url': 'https://example.com/images/room4.jpg'
            },
            {
                'name': 'Студия "Париж"',
                'description': 'Креативная студия для фото- и видеосъемки',
                'capacity': 5,
                'price_per_hour': 1500.0,
                'has_projector': False,
                'has_whiteboard': False,
                'has_video_conf': False,
                'is_active': True,
                'image_url': 'https://example.com/images/room5.jpg'
            }
        ]
    )


def downgrade():
    # Удаляем примеры комнат
    op.execute("DELETE FROM rooms WHERE name IN ('Переговорная \"Москва\"', 'Кабинет \"Токио\"', 'Конференц-зал \"Нью-Йорк\"', 'Рабочая зона \"Берлин\"', 'Студия \"Париж\"')")