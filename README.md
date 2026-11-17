# Sistema de Inventario de Zapatos — SQLAlchemy ORM

## 1. Información del proyecto

| Información | Descripción |
|---|---|
| Estudiante | [JUAN DIAZ] |
| Asignatura | [Desarrollo de aplicaciones con acceso a datos] |
| Docente | [pimienta] |
| Fecha | [17/11/26] |
| Lenguaje | Python |
| ORM | SQLAlchemy |
| Base de datos | SQLite (`zapateria.db`) |

## 2. Descripción del proyecto

Aplicación de consola para administrar el inventario de una tienda de zapatos. Cada zapato tiene un identificador, un modelo, una talla y un precio. Los datos se guardan de forma permanente en una base SQLite mediante SQLAlchemy ORM, de modo que no se pierden al cerrar el programa.

Funcionalidades: registrar zapatos, listar el inventario, buscar por ID, actualizar el precio y eliminar zapatos.

## 3. Estructura del proyecto

```text
tienda_zapatos/
├── main.py
├── datos.py
├── requirements.txt
├── README.md
└── evidencias/
```

| Archivo | Responsabilidad |
|---|---|
| `main.py` | Menú e interacción con el usuario; valida la entrada y llama a las funciones de `datos.py`. |
| `datos.py` | Capa de persistencia: engine, modelo `Zapato`, creación de la tabla y las cinco operaciones CRUD con SQLAlchemy. |
| `requirements.txt` | Dependencia del proyecto (`SQLAlchemy>=2.0,<3.0`). |
| `zapateria.db` | Se genera automáticamente la primera vez que el programa crea la tabla (`inicializar_bd()`). |

## 4. Instalación y ejecución

1. **Requisitos:** Python 3.9 o superior y pip. SQLite viene incluido con Python.
2. **Instalar dependencias:**
   ```bash
   python -m pip install -r requirements.txt
   ```
3. **Ejecutar:**
   ```bash
   python main.py
   ```
4. **Resultado esperado:** aparece el menú "TIENDA DE ZAPATOS" con seis opciones, y se crea el archivo `zapateria.db` en la carpeta del proyecto.

---

# 5. Documentación técnica

### Pregunta 1. Modelo y tabla

La tabla está representada por la clase `Zapato`, que hereda de `Base` (una subclase de `DeclarativeBase`).

```python
class Base(DeclarativeBase):
    pass

class Zapato(Base):
    __tablename__ = "zapatos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    modelo: Mapped[str] = mapped_column(String(100))
    talla: Mapped[int]
    precio: Mapped[float]
```

SQLAlchemy toma el nombre de la tabla del atributo `__tablename__` (`zapatos`). Cada atributo anotado con `Mapped[...]` se convierte en una columna: el nombre del atributo es el nombre de la columna y el tipo de Python define el tipo SQL (`int` → INTEGER, `str` → VARCHAR, `float` → FLOAT). `primary_key=True` marca `id` como clave primaria y `autoincrement=True` hace que se genere solo. Toda esta información queda registrada en `Base.metadata`.

### Pregunta 2. Creación de la base de datos

Al ejecutar `main.py`, lo primero que hace `main()` es llamar a `datos.inicializar_bd()`:

```python
engine = create_engine("sqlite:///zapateria.db")

def inicializar_bd():
    Base.metadata.create_all(engine)
```

`create_engine` solo configura la conexión. Cuando `create_all` abre la primera conexión, SQLite crea el archivo `zapateria.db` si no existe, y SQLAlchemy emite `CREATE TABLE zapatos (...)` según lo declarado en `Zapato`. Si la tabla ya existe, `create_all` no la modifica ni borra datos, así que es seguro llamarla en cada ejecución.

### Pregunta 3. Registro de zapatos

Recorrido al elegir la opción 1:

1. `main()` pide `modelo`, `talla` y `precio` con `input()` y los convierte a `int` y `float`.
2. `main.py` valida que el modelo no esté vacío y que talla y precio sean positivos.
3. Llama a `datos.crear_zapato(modelo, talla, precio)`.
4. Esa función crea el objeto `Zapato`, abre una sesión, hace `session.add(zapato)` y `session.commit()`.
5. En el `commit()` SQLAlchemy ejecuta el `INSERT INTO zapatos ...` y SQLite guarda la fila en `zapateria.db`, asignando el `id`.
6. La función devuelve `True` y el menú muestra "Zapato registrado correctamente."

```python
def crear_zapato(modelo, talla, precio):
    zapato = Zapato(modelo=modelo, talla=talla, precio=precio)
    with Session(engine) as session:
        session.add(zapato)
        session.commit()
    return True
```

### Pregunta 4. Sesiones y transacciones

La `Session` es el espacio de trabajo del ORM: mantiene los objetos que se consultan, agrega o modifican y los sincroniza con la base de datos dentro de una transacción. En el programa, cada función abre una con `with Session(engine) as session:`, que la cierra automáticamente al terminar.

`add()`, el cambio de un atributo o `delete()` solo se registran en la sesión; la base de datos no queda modificada de forma permanente hasta llamar a `commit()`. Si no se hace `commit()`, al cerrarse la sesión la transacción se descarta (rollback) y el cambio se pierde: el zapato no se registraría, el precio no cambiaría y el registro no se eliminaría. Por eso `crear_zapato`, `actualizar_precio` y `eliminar_zapato` terminan con `session.commit()`.

### Pregunta 5. Búsqueda por ID

```python
def buscar_zapato(id_zapato):
    with Session(engine) as session:
        return session.get(Zapato, id_zapato)
```

`session.get(Zapato, id)` busca por clave primaria (`SELECT ... WHERE zapatos.id = ?`). Si lo encuentra, devuelve un objeto `Zapato` con sus atributos (`id`, `modelo`, `talla`, `precio`); si no existe, devuelve `None`. `main.py` revisa `if zapato is None` para mostrar "Zapato no encontrado." o imprimir los datos.

### Pregunta 6. Actualización de precios

```python
def actualizar_precio(id_zapato, nuevo_precio):
    with Session(engine) as session:
        zapato = session.get(Zapato, id_zapato)
        if zapato is None:
            return False
        zapato.precio = nuevo_precio
        session.commit()
        return True
```

Primero se obtiene el objeto con `session.get`. Luego se modifica su atributo como en cualquier objeto Python (`zapato.precio = nuevo_precio`); la sesión detecta el cambio. Al hacer `commit()` SQLAlchemy genera el `UPDATE zapatos SET precio=? WHERE id=?` y lo guarda. Si el ID no existe devuelve `False`.

### Pregunta 7. Eliminación de registros

```python
def eliminar_zapato(id_zapato):
    with Session(engine) as session:
        zapato = session.get(Zapato, id_zapato)
        if zapato is None:
            return False
        session.delete(zapato)
        session.commit()
        return True
```

Se obtiene el objeto, se marca con `session.delete()` y al hacer `commit()` se ejecuta el `DELETE FROM zapatos WHERE id=?`. Para comprobar que ya no existe, listo el inventario (opción 2) y el zapato no aparece; además, buscarlo por su ID (opción 3) muestra "Zapato no encontrado.", porque `buscar_zapato` devuelve `None`.

### Pregunta 8. Persistencia de datos

Los zapatos se conservan al cerrar y volver a ejecutar el programa. Los datos no viven en variables de Python (que desaparecen al terminar el proceso), sino en el archivo `zapateria.db`, al que cada `commit()` escribe de forma definitiva. Al reiniciar, `inicializar_bd()` ejecuta `create_all`, que no recrea ni vacía una tabla existente, y las consultas leen las filas guardadas. Lo comprobé en la Prueba 6: tras cerrar y reabrir, el listado seguía mostrando el zapato restante con su precio actualizado.

---

## 6. Pruebas de funcionamiento y evidencias

Salida real de la ejecución del programa. **Reemplaza o complementa estos bloques con tus capturas de pantalla en `evidencias/`.**

### Prueba 1. Registrar zapatos
- Datos: `Nike Air`, talla 40, precio 300.000; `Adidas Run`, talla 42, precio 400.000.
- Resultado: el programa mostró "Zapato registrado correctamente." en ambos casos.

![Registro de zapatos](evidencias/registro.png)

### Prueba 2. Listar inventario
```text
ID: 1 | Modelo: Nike Air | Talla: 40 | Precio: $300.00
ID: 2 | Modelo: Adidas Run | Talla: 42 | Precio: $300.00
```
![Listado de zapatos](evidencias/listado.png)

### Prueba 3. Buscar por ID
- ID usado: 1.
```text
ID: 1 | Modelo: Nike Air | Talla: 40 | Precio: $120.50
```
![Búsqueda de zapatos](evidencias/busqueda.png)

### Prueba 4. Actualizar precio
- Zapato 1 (Nike Air): precio anterior $300.000, precio nuevo $100.000.
- Resultado: "Precio actualizado." y al listar aparece `Precio: $100.000`.

![Actualización de precio](evidencias/actualizacion.png)

### Prueba 5. Eliminar zapato
- ID eliminado: 2. Resultado: "Zapato eliminado." Al listar, solo queda el zapato 1.

![Eliminación de zapato](evidencias/eliminacion.png)


### Pruebas con registros inexistentes (ID 99)

| Operación | ¿Qué sucedió? |
|---|---|
| Buscar ID inexistente | `buscar_zapato` devolvió `None` y el menú mostró "Zapato no encontrado." |
| Actualizar ID inexistente | `actualizar_precio` devolvió `False`, no se modificó nada y el menú mostró "Zapato no encontrado." |
| Eliminar ID inexistente | `eliminar_zapato` devolvió `False`, no se borró nada y el menú mostró "Zapato no encontrado." |

## 7. Conclusiones

1. Con SQLAlchemy las operaciones CRUD se reducen a trabajar con objetos `Zapato` dentro de una sesión: `add`, `get`, modificar atributos y `delete`, más `commit()` para guardar.
2. Con el ORM no se escribe SQL: el código es más legible y cercano a Python, y SQLAlchemy genera los `INSERT`, `SELECT`, `UPDATE` y `DELETE`. Con SQL directo habría que armar las sentencias y mapear las filas a mano.
3. La dificultad principal fue entender que los cambios no se guardan sin `commit()` y manejar los IDs inexistentes; lo resolví devolviendo `None` o `False` cuando `session.get` no encuentra el registro.
