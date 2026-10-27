"""API de comentarios: guarda el mismo comentario en DynamoDB y S3 (ingesta push)."""
import json
import os
import uuid
from datetime import datetime, timezone

import boto3


def lambda_handler(event, context):
    # Soporta el evento directo del API Gateway (integración lambda del taller)
    # y pruebas con un evento cuyo body sea JSON.
    try:
        payload = event
        if isinstance(event, dict) and "body" in event:
            payload = event["body"]
        if isinstance(payload, str):
            payload = json.loads(payload)
        if not isinstance(payload, dict):
            return {"statusCode": 400, "message": "Se requiere un objeto JSON"}

        tenant_id = payload.get("tenant_id")
        texto = payload.get("texto")
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            return {"statusCode": 400, "message": "tenant_id es obligatorio"}
        if not isinstance(texto, str) or not texto.strip():
            return {"statusCode": 400, "message": "texto es obligatorio"}
    except (ValueError, TypeError, AttributeError):
        return {"statusCode": 400, "message": "JSON inválido"}

    table_name = os.environ["TABLE_NAME"]
    bucket_name = os.environ["BUCKET_NAME"]
    # UUID v1, igual que el ejemplo del taller del profesor.
    comentario_id = str(uuid.uuid1())
    documento = {
        "tenant_id": tenant_id,
        "uuid": comentario_id,
        "texto": texto,
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
    }
    key = f"comentarios/{comentario_id}.json"

    try:
        # DynamoDB: mantiene la funcionalidad original del taller.
        boto3.resource("dynamodb").Table(table_name).put_item(Item={
            "tenant_id": tenant_id,
            "uuid": comentario_id,
            "detalle": json.dumps({"texto": texto}, ensure_ascii=False),
        })
        # S3: añade ingesta push en el bucket del stage indicado por el entorno.
        boto3.client("s3").put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(documento, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
        )
    except Exception:
        # No filtrar errores internos ni credenciales en la respuesta pública.
        print("Error al escribir el comentario en DynamoDB o S3")
        raise

    return {
        "statusCode": 201,
        "message": "Comentario guardado en DynamoDB y S3",
        "tenant_id": tenant_id,
        "uuid": comentario_id,
        "bucket": bucket_name,
        "key": key,
    }
