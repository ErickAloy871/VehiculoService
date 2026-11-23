"""Consultas SQLAlchemy para la gestión de compradores."""
from sqlalchemy import select, or_
from app.models import Comprador


class CompradorRepository:

    def __init__(self, db):
        self.db = db

    def por_id(self, id: int) -> Comprador | None:
        """Busca un comprador por su clave primaria."""
        return self.db.get(Comprador, id)

    def listar_por_usuario(self, usuario: str) -> list[Comprador]:
        """Lista los compradores creados por el usuario autenticado."""
        stmt = (
            select(Comprador)
            .where(Comprador.usuario == usuario)
            .order_by(Comprador.id.desc())
        )
        return list(self.db.scalars(stmt).all())

    def buscar(self, usuario: str, texto: str) -> list[Comprador]:
        """Busca compradores por nombre o documento, restringido al usuario."""
        cadena = f"%{texto.strip()}%"
        stmt = (
            select(Comprador)
            .where(
                Comprador.usuario == usuario,
                or_(
                    Comprador.nombre.ilike(cadena),
                    Comprador.documento.ilike(cadena)
                )
            )
            .order_by(Comprador.id.desc())
        )
        return list(self.db.scalars(stmt).all())

