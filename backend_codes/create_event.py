import json
import boto3
import uuid
from datetime import datetime

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
        body = json.loads(event.get("body") or "{}")

        required = ["name", "email", "phone", "eventId", "tier"]
        missing = [f for f in required if not body.get(f)]
        if missing:
            return response(400, {"message": f"Missing fields: {', '.join(missing)}"})

        # Check event exists and has seats
        ev = events_table.get_item(Key={"eventId": body["eventId"]}).get("Item")
        if not ev:
            return response(404, {"message": "Event not found"})

        seats_left = int(ev["seatsTotal"]) - int(ev["seatsTaken"])
        if seats_left <= 0:
            return response(409, {"message": "No seats available"})

        reg = {
            "registrationId": "REG-" + uuid.uuid4().hex[:6].upper(),
            "name": body["name"],
            "email": body["email"],
            "phone": body["phone"],
            "eventId": body["eventId"],
            "tier": body["tier"],
            "status": "CONFIRMED",
            "createdAt": datetime.utcnow().isoformat(),
        }

        registrations_table.put_item(Item=reg)

        # Increment seatsTaken atomically
        events_table.update_item(
            Key={"eventId": body["eventId"]},
            UpdateExpression="SET seatsTaken = seatsTaken + :inc",
            ConditionExpression="seatsTaken < seatsTotal",
            ExpressionAttributeValues={":inc": 1},
        )

        return response(201, reg)

    except events_table.meta.client.exceptions.ConditionalCheckFailedException:
        return response(409, {"message": "No seats available"})
    except Exception as e:
        return response(500, {"message": str(e)})

def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": HEADERS,
        "body": json.dumps(body, default=str),
    }
