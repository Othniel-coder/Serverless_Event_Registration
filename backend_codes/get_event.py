import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Events")

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
}

def lambda_handler(event, context):
    event_id = (event.get("pathParameters") or {}).get("id")

    try:
        if event_id:
            result = table.get_item(Key={"eventId": event_id})
            item = result.get("Item")
            if not item:
                return response(404, {"message": "Event not found"})
            return response(200, item)
        else:
            result = table.scan()
            return response(200, result.get("Items", []))  # ← must return Items array

    except Exception as e:
        return response(500, {"message": str(e)})

def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": HEADERS,
        "body": json.dumps(body, default=str),
    }
