from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
#load_dotenv()

# Initialize Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS

# Initialize the SNS client
sns_client = boto3.client('sns', region_name='ap-south-1')  # Replace with your AWS region

# Define your topic ARN (if using topics)
TOPIC_ARN = 'arn:aws:sns:ap-south-1:107335645910:bbbbb'  # Replace with your SNS Topic ARN

def send_sms(phone_number, message):
    try:
        if phone_number:
            # Sending directly to a phone number
            response = sns_client.publish(
                PhoneNumber=phone_number,
                Message=message
            )
        else:
            # Sending to an SNS topic
            response = sns_client.publish(
                TopicArn=TOPIC_ARN,
                Message=message
            )
        
        # Log response for debugging
        print(f"Response: {response}")
        
        # Check for successful response
        if response.get('MessageId'):
            return {"status": "success", "MessageId": response['MessageId']}
        else:
            return {"status": "failure", "error": "MessageId not returned"}
            
    except NoCredentialsError:
        return {"status": "error", "message": "AWS credentials not found."}
    except PartialCredentialsError:
        return {"status": "error", "message": "Incomplete AWS credentials provided."}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_sms', methods=['POST'])
def send_sms_endpoint():
    data = request.get_json()
    phone_number = data.get('phone_number')
    message = data.get('message')
    
    if not message:
        return jsonify({"status": "error", "message": "Message is required."}), 400

    response = send_sms(phone_number, message)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
