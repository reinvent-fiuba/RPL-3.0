## Documentación del contenedor de desarrollo

La db configurada en metaservices.dev.yml es distinta a la del dir root  (metaservices.local.yml) para que se utilice la dev en los tests dentro del devcontainer. La de metaservices.local.yml es la que se usa para pruebas manuales del back.

- Dentro del devcontainer, para correr los tests:

```bash
python -m pytest
```

- Dentro del devcontainer, para correr el servidor (acceso en `http://localhost:<puerto>/docs`):

```bash
fastapi run rpl_activities/src/main.py --port 9000
# o
fastapi run rpl_users/src/main.py --port 9001
``` 


