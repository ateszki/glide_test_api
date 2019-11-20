import pytest

def test_office(client):
    response = client.get('/offices/1')
    request_office = response.json
    office = {
              "address": "450 Market St", 
              "city": "San Francisco", 
              "country": "United States", 
              "id": 1
            }
    assert  request_office["id"] == office["id"]

def test_offices(client):
    response = client.get('/offices')
    request_offices = response.json
    office =   {
            "address": "20 W 34th St", 
            "city": "New York", 
            "country": "United States", 
            "id": 2
          }
    assert request_offices[1]["id"] == office["id"]
    assert len(request_offices) == 5

def test_department(client):
    response = client.get('/departments/1')
    request_dpt = response.json
    dpt = {
            "id": 1,
            "name": "Sales",
            "superdepartment": None
        }
    assert  request_dpt["id"] == dpt["id"]

def test_departments(client):
    response = client.get('/departments')
    request_dpts = response.json
    dpt =   {
            "id": 6,
            "name": "Outbound Sales",
            "superdepartment": 1
        }
    assert request_dpts[5]["id"] == dpt["id"]
    assert len(request_dpts) == 10

def test_departments_limit_offset(client):
    response = client.get('/departments?limit=5&offset=5')
    request_dpts = response.json
    dpt =   {
            "id": 6,
            "name": "Outbound Sales",
            "superdepartment": 1
        }
    assert request_dpts[0]["id"] == dpt["id"]
    assert len(request_dpts) == 5

def test_departments_expand(client):
    response = client.get('/departments?expand=superdepartment')
    request_dpts = response.json
    dpt =   {
            "id": 6,
            "name": "Outbound Sales",
            "superdepartment": 1
        }
    assert request_dpts[5]["superdepartment"]["id"] == dpt["superdepartment"]

def test_employee(client):
    response = client.get('/employees/1')
    request_employee = response.json
    
    employee = {
          "department": 5, 
          "first": "Patricia", 
          "id": 1, 
          "last": "Diaz", 
          "manager": None, 
          "office": 2
        }
    assert  request_employee["id"] == employee["id"]

def test_employees(client):
    response = client.get('/employees')
    request_employees = response.json
    
    employee = {
            "department": 6, 
            "first": "Ruth", 
            "id": 4, 
            "last": "Morgan", 
            "manager": None, 
            "office": 2
          }
    assert  request_employees[3]["id"] == employee["id"]
    assert len(request_employees) == 100

def test_employees_limit_offset(client):
    response = client.get('/employees?limit=5&offset=3')
    request_employees = response.json
    
    employee = {
            "department": 6, 
            "first": "Ruth", 
            "id": 4, 
            "last": "Morgan", 
            "manager": None, 
            "office": 2
          }
    assert  request_employees[0]["id"] == employee["id"]
    assert len(request_employees) == 5

def test_employees_expand(client):
    response = client.get('/employees?expand=manager')
    request_employees = response.json
    
    employee = {
        "department": 5, 
        "first": "Daniel", 
        "id": 2, 
        "last": "Smith", 
        "manager": 1, 
        "office": 2
      }
  
    assert  request_employees[1]["manager"]["id"] == employee["manager"]
