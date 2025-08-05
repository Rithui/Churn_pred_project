from flask import Flask, render_template, request, jsonify
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
API_URL = "http://127.0.0.1:8000"

@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            # Get form data
            data = {
                "tenure": float(request.form['tenure']),
                "MonthlyCharges": float(request.form['monthlyCharges']),
                "TotalCharges": float(request.form['totalCharges']),
                "gender": request.form['gender'],
                "InternetService": request.form['internetService'],
                "Contract": request.form['contract'],
                "PaymentMethod": request.form['paymentMethod']
            }

            logger.debug(f"Sending data to API: {json.dumps(data, indent=2)}")

            # Make prediction request
            try:
                response = requests.post(f"{API_URL}/predict", json=data)
                logger.debug(f"API Response Status: {response.status_code}")
                logger.debug(f"API Response Content: {response.text}")

                if response.status_code != 200:
                    error_detail = response.json().get('detail', 'Unknown error')
                    logger.error(f"API Error: {error_detail}")
                    return f"API Error: {error_detail}", response.status_code

                result = response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"API Request Error: {str(e)}")
                return render_template('error.html',
                                       error="Failed to connect to prediction service. Please try again later."), 500

            # Get chart data
            try:
                chart_response = requests.get(f"{API_URL}/chart-data")
                chart_data = chart_response.json() if chart_response.status_code == 200 else {
                    "feature_importance": [],
                    "churn_by_contract": []
                }
            except requests.exceptions.RequestException as e:
                logger.error(f"Chart Data Error: {str(e)}")
                chart_data = {
                    "feature_importance": [],
                    "churn_by_contract": []
                }

            return render_template('result.html',
                                   prediction=result.get('churn_probability', 0),
                                   feature_importance=chart_data.get('feature_importance', []),
                                   churn_by_contract=chart_data.get('churn_by_contract', []))
        except KeyError as e:
            logger.error(f"Missing form field: {str(e)}")
            return render_template('error.html',
                                   error=f"Missing required field: {str(e)}"), 400
        except ValueError as e:
            logger.error(f"Invalid value in form: {str(e)}")
            return render_template('error.html',
                                   error=f"Invalid value provided: {str(e)}"), 400
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return render_template('error.html',
                                   error="An unexpected error occurred. Please try again."), 500

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
