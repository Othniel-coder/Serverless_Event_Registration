import json
import boto3

dynamodb = boto3.resource("dynamodb")
registrations_table = dynamodb.Table("Registrations")

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
}


ALLOWED_STATUSES = {"CONFIRMED", "CANCELLED", "PENDING"}

def lambda_handler(event, context):
    try:
        registration_id = (event.get("pathParameters") or {}).get("id")
        if not registration_id:
            return response(400, {"message": "Missing registrationId in path"})

        body = json.loads(event.get("body") or "{}")
        status = body.get("status", "").upper()

        if status not in ALLOWED_STATUSES:
            return response(400, {"message": f"Invalid status. Must be one of: {', '.join(ALLOWED_STATUSES)}"})

        result = registrations_table.update_item(
            Key={"registrationId": registration_id},
            UpdateExpression="SET #s = :status",
            ConditionExpression="attribute_exists(registrationId)",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":status": status},
            ReturnValues="ALL_NEW",
        )

        return response(200, result["Attributes"])

    except registrations_table.meta.client.exceptions.ConditionalCheckFailedException:
        return response(404, {"message": "Registration not found"})
    except Exception as e:
        return response(500, {"message": str(e)})

def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": HEADERS,
        "body": json.dumps(body, default=str),
    }
