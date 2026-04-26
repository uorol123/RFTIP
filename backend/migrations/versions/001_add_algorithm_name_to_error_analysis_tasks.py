"""add algorithm_name to error_analysis_tasks

Revision ID: 001_add_algorithm_name
Revises:
Create Date: 2024-03-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001_add_algorithm_name'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """添加 algorithm_name 字段到 error_analysis_tasks 表"""
    # 添加 algorithm_name 字段
    op.add_column(
        'error_analysis_tasks',
        sa.Column('algorithm_name', sa.String(50), nullable=True, comment='算法名称', server_default='gradient_descent')
    )

    # 为现有数据设置默认值
    op.execute(
        "UPDATE error_analysis_tasks SET algorithm_name = 'gradient_descent' WHERE algorithm_name IS NULL"
    )


def downgrade() -> None:
    """移除 algorithm_name 字段"""
    op.drop_column('error_analysis_tasks', 'algorithm_name')
