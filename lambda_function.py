import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Expenses')

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))  # For debugging

    try:
        method = event["requestContext"]["http"]["method"]

        if method == 'POST':
            data = json.loads(event['body'])
            expense_id = str(uuid.uuid4())
            table.put_item(Item={"expense_id": expense_id, **data})
            return {
                "statusCode": 201,
                "body": json.dumps({"message": "Expense added", "id": expense_id})
            }

        elif method == 'GET':
            expense_id = event['queryStringParameters']['expense_id']
            response = table.get_item(Key={"expense_id": expense_id})
            return {
                "statusCode": 200,
                "body": json.dumps(response.get("Item", {}))
            }

        elif method == 'PUT':
            data = json.loads(event['body'])
            expense_id = data['expense_id']
            table.update_item(
                Key={"expense_id": expense_id},
                UpdateExpression="SET amount=:a, category=:c, date=:d",
                ExpressionAttributeValues={
                    ":a": data['amount'],
                    ":c": data['category'],
                    ":d": data['date']
                }
            )
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Expense updated"})
            }

        elif method == 'DELETE':
            expense_id = event['queryStringParameters']['expense_id']
            table.delete_item(Key={"expense_id": expense_id})
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Expense deleted"})
            }

        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Unsupported HTTP method"})
        }

    except Exception as e:
        print("Error occurred:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal Server Error", "error": str(e)})
        }
