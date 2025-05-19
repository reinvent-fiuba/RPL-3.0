## Plan de migración

> [!WARNING]\
> Aca solo se documenta la parte local del proceso de migración. El resto se encuentra documentado en los archivos del proyecto en drive.

- Cargar el dump en una imagen limpia de mysql 8.0.37 (CONFIGURADA CON `character_set_server=latin1` y `collation_server=latin1_swedish_ci`)

- Aplicar con alembic: Cambios varchar a text (mover solo el `script de alembic` que corresponde al dir versions y luego `python -m alembic upgrade head`)

- Aplicar el `script aux` para alterar todas las tablas a utf8mb4

- Reconfigurar dockerfile: `character_set_server=utf8mb4` y `collation_server=utf8mb4_0900_ai_ci`, reiniciar el container con la db y describir las tablas para verificar.

- Exportar dumps de tablas especificas separadas:    
    - `mysqldump -p --no-create-info rpl courses users course_users roles permissions validation_token > /var/lib/mysql/users_data.sql`     (el path con /var/lib/mysql es para poder sacarlo con el volumen que ya tiene y no crear otro)
    - `mysqldump -p --no-create-info rpl activities activity_categories activity_submissions rpl_files io_tests unit_tests test_run io_test_run unit_test_run results > /var/lib/mysql/activities_data.sql`

- Cargar los dumps en una imagen limpia de mysql 8.4.3:
    - Crear manualmente las dbs: `rpl_users` y `rpl_activities`
    - Usar los `scripts aux` para crear las tablas de esas dbs
    - `mysql -p rpl_users < users_data.sql`
    - `mysql -p rpl_activities < activities_data.sql`
    - Usar el `script aux` para renombrar tablas inconsistentes y arreglar columnas adicionales.
    - Revision

- Exportar dbs con el formato requerido por gcp: 
    - `mysqldump --databases rpl_users –user=root -p --hex-blob --single-transaction --set-gtid-purged=OFF --default-character-set=utf8mb4 > rpl_users.sql`
    - `mysqldump --databases rpl_activities –user=root -p --hex-blob --single-transaction --set-gtid-purged=OFF --default-character-set=utf8mb4 > rpl_activities.sql`


