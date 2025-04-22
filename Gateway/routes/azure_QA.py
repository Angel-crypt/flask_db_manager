from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import requests
import os

load_dotenv()

azure_QA = Blueprint('azure_QA', __name__)

AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')
AZURE_API_KEY = os.getenv('AZURE_KEY')
AZURE_PARAMS = {
    "projectName": os.getenv('AZURE_PROJECT_NAME'),
    "api-version": os.getenv('AZURE_API_VERSION'),
    "deploymentName": os.getenv('AZURE_DEPLOYMENT_NAME'),
}

@azure_QA.route('/qa', methods=['POST'])
def ask_question():
    try:
        question_data = request.get_json()

        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.post(
            AZURE_ENDPOINT,
            headers=headers,
            params=AZURE_PARAMS,
            json=question_data
        )

        # Devolver solo los answers directamente
        if response.status_code == 200:
            result = response.json()
            answers = result.get("answers", [])
            if answers:
                return jsonify({"answer": answers[0].get("answer")})
            else:
                return jsonify({"answer": None})
        else:
            return jsonify({"error": "Azure API error", "details": response.text}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500