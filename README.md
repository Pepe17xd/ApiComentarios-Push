# api-comentario — Ingesta Push S3 por stage

Adaptación del ejercicio **Taller 4, Semana 11**. Despliega una API REST con DynamoDB y bucket S3 independientes para `dev`, `test` y `prod`. Cada comentario se graba en DynamoDB y como JSON en `s3://<bucket>/comentarios/<uuid>.json`.

## Antes de desplegar

1. Confirmar que AWS Academy está activo y las credenciales AWS de tu VM son válidas (`aws sts get-caller-identity`).
2. Confirmar que el `org` de Serverless y el ARN `LabRole` de `serverless.yml` siguen siendo correctos **para tu cuenta**. Estos valores fueron tomados del archivo compartido; no son portables a otra cuenta.
3. Confirmar que `LabRole` tiene `dynamodb:PutItem` y `s3:PutObject`; este proyecto **no modifica IAM** porque AWS Academy restringe esa acción en muchos laboratorios.
4. Verificar que los nombres S3 sean globalmente únicos. Si ya existen fuera de la cuenta, cambiar el sufijo en `BUCKET_NAME`.
5. Si ya existen despliegues de `api-comentario`, revisa el estado de sus stacks antes de actualizarlos. No borres tablas con datos importantes.

## Despliegue

Desde la carpeta del proyecto:

```bash
serverless print --stage dev
serverless deploy --stage dev
serverless info --stage dev
serverless deploy --stage test
serverless deploy --stage prod
```

El endpoint de cada stage será mostrado por `serverless info --stage dev|test|prod`. **No uses las URL del proyecto anterior `api-s3`.**

## Prueba

`POST` a `/comentario/crear`, con `Content-Type: application/json` y cuerpo de `ejemplo-comentario.json`:

```bash
curl -X POST 'URL_REAL_DEL_ENDPOINT' \
  -H 'Content-Type: application/json' \
  --data-binary @ejemplo-comentario.json
```

Comprueba las tablas en DynamoDB y los objetos en S3:

```bash
aws s3 ls s3://api-comentario-ingesta-dev-521119692025/comentarios/
```

**Nota sobre la integración:** se conserva `integration: lambda` del profesor. API Gateway puede devolver HTTP 200 aunque el cuerpo incluya `statusCode: 201`; ese campo es parte del JSON, no necesariamente el código HTTP de la respuesta. La función lanza errores de escritura para evitar confirmar falsamente un guardado.

**Nota de consistencia:** esta implementación hace primero la escritura en DynamoDB y después en S3. Si S3 falla, el registro DynamoDB puede persistir: no son una transacción atómica.

## Evidencias

Captura el despliegue por stage, la petición curl/Postman, la tabla DynamoDB, los tres buckets S3 y el JSON alojado en cada uno.

## Limpieza (solo cuando ya tengas evidencias)

Los buckets S3 creados por CloudFormation **deben estar vacíos** para que `serverless remove` pueda borrarlos. Vacía **solo** los buckets creados por este ejercicio (si no tienen versionado):

```bash
aws s3 rm s3://api-comentario-ingesta-dev-521119692025 --recursive
aws s3 rm s3://api-comentario-ingesta-test-521119692025 --recursive
aws s3 rm s3://api-comentario-ingesta-prod-521119692025 --recursive
serverless remove --stage dev
serverless remove --stage test
serverless remove --stage prod
```

Si aparece un error, no ejecutes borrados amplios sobre otros recursos. Los comandos `serverless remove` también eliminan las tablas DynamoDB administradas por esos stacks, con sus datos.

## Procedencia y alcance

Se usaron `serverless.yml` compartido en la conversación y el material del docente. El contenido **original** de `comentario.py` no fue proporcionado, así que se reconstruyó una implementación compatible con los campos `tenant_id`, `texto`, clave compuesta `tenant_id`/`uuid`, tabla DynamoDB y el nuevo requerimiento S3. Compárala con la función original antes de reemplazar un repositorio con cambios propios.
