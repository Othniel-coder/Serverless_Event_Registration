import json
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = "Registrations"  # replace with your actual table name
table = dynamodb.Table(TABLE_NAME)

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
}


def lambda_handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        email = params.get("email")

        if email:
            # filter registrations by email
            response = table.scan(
                FilterExpression=Attr("email").eq(email)
            )
        else:
            # return all registrations (admin)
            response = table.scan()

        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps(response["Items"]),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": HEADERS,
            "body": json.dumps({"error": str(e)}),
        }
