"""Migración S13 (reintentos con espera progresiva) y E18 (outbox transaccional)."""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    # S13: Columnas de reintentos con espera progresiva
    op.add_column("ventas", sa.Column("intentos", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("ventas", sa.Column("proximo_intento_utc", sa.DateTime(), nullable=True))

    # E18: Tabla de outbox de eventos
    # Usamos bind para evitar error si la tabla fue creada previamente
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if "outbox_eventos" not in inspector.get_table_names():
        op.create_table(
            "outbox_eventos",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("evento_id", sa.String(36), nullable=False, unique=True),
            sa.Column("tipo", sa.String(50), nullable=False),
            sa.Column("payload", sa.Text(), nullable=False),
            sa.Column("estado", sa.String(20), nullable=False, server_default="PENDIENTE"),
            sa.Column("intentos", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("ultimo_error", sa.String(255), nullable=True),
            sa.Column("creado_en", sa.DateTime(), nullable=False),
            sa.Column("enviado_en", sa.DateTime(), nullable=True),
        )


def downgrade():
    op.drop_table("outbox_eventos")
    op.drop_column("ventas", "proximo_intento_utc")
    op.drop_column("ventas", "intentos")

