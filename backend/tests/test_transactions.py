import pytest
from datetime import datetime
from app import schemas, models

@pytest.mark.parametrize(
    "amount,expected_category",
    [
        (100.0, models.TransactionCategoryEnum.INCOME),
        (-10.0, models.TransactionCategoryEnum.UNCATEGORIZED),
    ]
)
def test_create_transaction(client, db, test_user, test_token, amount, expected_category):
    """Test creating a transaction"""
    response = client.post(
        "/api/v1/transactions/",
        json={
            "date": "2025-05-01T00:00:00",
            "description": "Test Transaction",
            "amount": amount,
            "raw_text": "Test raw text"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == expected_category.value


def test_transaction_auto_categorization(client, db, test_user, test_token):
    """Test automatic categorization with rules"""
    # Create a test rule
    rule_data = {
        "name": "Test Rule",
        "pattern": "test",
        "category": models.TransactionCategoryEnum.FOOD_DRINK.value,
        "priority": 100,
        "is_active": True
    }
    
    response = client.post(
        "/api/v1/transactions/rules/",
        json=rule_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    
    # Create a transaction that matches the rule
    response = client.post(
        "/api/v1/transactions/",
        json={
            "date": "2025-05-01T00:00:00",
            "description": "Test Food Transaction",
            "amount": -20.0,
            "raw_text": "Test raw text"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == models.TransactionCategoryEnum.FOOD_DRINK.value


def test_transaction_rules_crud(client, db, test_user, test_token):
    """Test CRUD operations for transaction rules"""
    # Create a rule
    rule_data = {
        "name": "Test Rule",
        "pattern": "test",
        "category": models.TransactionCategoryEnum.FOOD_DRINK.value,
        "priority": 100,
        "is_active": True
    }
    
    response = client.post(
        "/api/v1/transactions/rules/",
        json=rule_data,
        headers={"Authorization": f"Bearer {test_token}"
    )
    assert response.status_code == 200
    created_rule = response.json()
    
    # Get the rule
    response = client.get(
        f"/api/v1/transactions/rules/{created_rule['id']}/",
        headers={"Authorization": f"Bearer {test_token}"
    )
    assert response.status_code == 200
    retrieved_rule = response.json()
    assert retrieved_rule == created_rule
    
    # Update the rule
    update_data = {
        "name": "Updated Rule",
        "priority": 50
    }
    response = client.put(
        f"/api/v1/transactions/rules/{created_rule['id']}/",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"
    )
    assert response.status_code == 200
    updated_rule = response.json()
    assert updated_rule["name"] == "Updated Rule"
    assert updated_rule["priority"] == 50
    
    # Delete the rule
    response = client.delete(
        f"/api/v1/transactions/rules/{created_rule['id']}/",
        headers={"Authorization": f"Bearer {test_token}"
    )
    assert response.status_code == 200


def test_monthly_summary(client, db, test_user, test_token):
    """Test monthly spending summary"""
    # Create some test transactions
    transactions = [
        {
            "date": "2025-05-01T00:00:00",
            "description": "Food Expense",
            "amount": -50.0,
            "category": models.TransactionCategoryEnum.FOOD_DRINK.value
        },
        {
            "date": "2025-05-02T00:00:00",
            "description": "Transport Expense",
            "amount": -30.0,
            "category": models.TransactionCategoryEnum.TRANSPORT.value
        }
    ]
    
    for transaction in transactions:
        response = client.post(
            "/api/v1/transactions/",
            json=transaction,
            headers={"Authorization": f"Bearer {test_token}"
        )
        assert response.status_code == 200
    
    # Get monthly summary
    response = client.get(
        "/api/v1/transactions/summary/2025/5",
        headers={"Authorization": f"Bearer {test_token}"
    )
    assert response.status_code == 200
    summary = response.json()
    
    # Verify the summary
    categories = {item["category"]: item["total_amount"] for item in summary["summary"]}
    assert categories[models.TransactionCategoryEnum.FOOD_DRINK.value] == -50.0
    assert categories[models.TransactionCategoryEnum.TRANSPORT.value] == -30.0
