# Import the required modules
import pytest
from fastapi.testclient import TestClient

from src.main import app  # replace with actual script containing your FastAPI app

# Create a TestClient instance to simulate HTTP requests
client = TestClient(app)


def test_check_email_success():
    valid_address = "valid@gmail.com"
    # Make a POST request to the email validation endpoint with a valid email address
    response = client.post(
        f"/api/v1/tools/email-validation?email_address={valid_address}"
    )
    # Check if the HTTP status code is 200 (OK)
    assert response.status_code == 200
    # Parse the response body as JSON
    data = response.json()
    # Assert that the 'valid' field in the response is True
    assert data["valid"] == True
    # Assert that the 'normalized' field in the response matches the input email address
    assert data["normalized"] == valid_address


def test_check_email_failure():
    invalid_address = "invalid@example"
    # Make a POST request to the email validation endpoint with an invalid email address
    response = client.post(
        f"/api/v1/tools/email-validation?email_address={invalid_address}"
    )
    # Check if the HTTP status code is 400 (Bad Request)
    assert response.status_code == 400
    # Parse the response body as JSON
    data = response.json()
    # Assert that the 'valid' field in the response is False
    assert data["detail"]["valid"] == False
    # Assert that the 'email_address' field in the response matches the input email address
    assert data["detail"]["email_address"] == "invalid@example"


def test_check_email_no_email():
    # Make a POST request to the email validation endpoint without providing an email address
    response = client.post(f"/api/v1/tools/email-validation?email_address=")
    # Check if the HTTP status code is 400 (Bad Request)
    assert response.status_code == 400


def test_check_email_not_a_string():
    # Make a POST request to the email validation endpoint with an email address that is not a string
    response = client.post(f"/api/v1/tools/email-validation?email_address=1234")
    # Check if the HTTP status code is 400 (Bad Request)
    assert response.status_code == 400
