
### Tras todas las migraciones: Para generar clases a partir de la base de datos

Se pueden generar clases actualizadas para SQLAlchemy 2.0 a partir de la base de datos con la utilidad `sqlacodegen`:

```bash
# Dentro del devcontainer
# La opcion --pre es requerida en la fecha (2025-02) para instalar la version 3.0.0rc5 que soporta SQLAlchemy 2.0
pip install --pre sqlacodegen
sqlacodegen mysql+pymysql://root:rootpassword@latest_db:3306/rpl_activities > generated_activities_models.py
sqlacodegen mysql+pymysql://root:rootpassword@latest_db:3306/rpl_users > generated_users_models.py
```

Luego se puede editar el output para hacerlo mas agnostico con respecto a la base de datos y para usar los tipos recomendados por SQLAlchemy (por ejemplo, cambiar `TINYINT` por `Boolean`, u omisiones de tamaño para los strings). 

Ver: 
- [SQLAlchemy Type Hierarchy](https://docs.sqlalchemy.org/en/20/core/type_basics.html).
- [sqlacodegen repository](https://github.com/agronholm/sqlacodegen).
