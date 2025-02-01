## Documentación del contenedor de desarrollo

La db configurada en metaservices.dev.yml es distinta a la del dir root  (metaservices.local.yml) para que se utilice la dev en los tests dentro del devcontainer. La de metaservices.local.yml es la que se usa para pruebas manuales del back.

- Dentro del devcontainer, para correr los tests:

[TODO]


<!-- ```bash
pytest
``` -->


- Dentro del devcontainer, para correr el servidor (acceso en `http://localhost:9000/docs`):

```bash
fastapi run --reload --port 80
``` 


