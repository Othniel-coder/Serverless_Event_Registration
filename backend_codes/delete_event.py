import json
import boto3

dynamodb = boto3.resource("dynamodb")
registrations_table = dynamodb.Table("Registrations")
events_table = dynamodb.Table("Events")

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
}


def lambda_handler(event, context):
    try:
        registration_id = (event.get("pathParameters") or {}).get("id")
        if not registration_id:
            return response(400, {"message": "Missing registrationId in path"})

        # Fetch registration first to get eventId for seat decrement
        existing = registrations_table.get_item(Key={"registrationId": registration_id}).get("Item")
        if not existing:
            return response(404, {"message": "Registration not found"})

        registrations_table.delete_item(
            Key={"registrationId": registration_id},
            ConditionExpression="attribute_exists(registrationId)",
        )

        # Decrement seatsTaken only if status was CONFIRMED
        if existing.get("status") == "CONFIRMED":
            events_table.update_item(
                Key={"eventId": existing["eventId"]},
                UpdateExpression="SET seatsTaken = if_not_exists(seatsTaken, :zero) - :dec",
                ConditionExpression="seatsTaken > :zero",
                ExpressionAttributeValues={":dec": 1, ":zero": 0},
            )

        return response(200, {"message": "Registration deleted", "registrationId": registration_id})

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
