
from sqlalchemy import create_engine, select, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    Session
)


engine = create_engine("sqlite:///zapateria.db")


class Base(DeclarativeBase):
    pass



class Zapato(Base):
    __tablename__ = "zapatos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    modelo: Mapped[str] = mapped_column(String(100))
    talla: Mapped[int]
    precio: Mapped[float]

    def __repr__(self):
        return (f"Zapato(id={self.id}, modelo={self.modelo!r}, "
                f"talla={self.talla}, precio={self.precio})")


def inicializar_bd():
    # Crea la tabla "zapatos" si todavia no existe.
    Base.metadata.create_all(engine)



def crear_zapato(modelo, talla, precio):
    zapato = Zapato(modelo=modelo, talla=talla, precio=precio)
    with Session(engine) as session:
        session.add(zapato)
        session.commit()
    return True


def listar_zapatos():
    with Session(engine) as session:
        return list(session.scalars(select(Zapato).order_by(Zapato.id)).all())



def buscar_zapato(id_zapato):
    with Session(engine) as session:
        # get() devuelve el objeto o None si no existe.
        return session.get(Zapato, id_zapato)



def actualizar_precio(id_zapato, nuevo_precio):
    with Session(engine) as session:
        zapato = session.get(Zapato, id_zapato)
        if zapato is None:
            return False
        zapato.precio = nuevo_precio
        session.commit()
        return True


def eliminar_zapato(id_zapato):
    with Session(engine) as session:
        zapato = session.get(Zapato, id_zapato)
        if zapato is None:
            return False
        session.delete(zapato)
        session.commit()
        return True
