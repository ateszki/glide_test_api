import os
from flask import (
    Blueprint, current_app, request, jsonify, json
)
from werkzeug.exceptions import abort
import requests
from dotty_dict import dotty

bp = Blueprint('api', __name__)

data = {
    'departments': None,
    'offices': None,
    'managers': [],
    'expands': [],
}


@bp.before_app_request
def load_data():
    departments_filename = os.path.join(current_app.static_folder, 'data', 'departments.json')
    with open(departments_filename) as departments:
        data['departments'] = json.load(departments)

    offices_filename = os.path.join(current_app.static_folder, 'data', 'offices.json')
    with open(offices_filename) as offices:
        data['offices'] = json.load(offices)

    data['expands'] = request.args.getlist('expand') if request.args.get('expand') is not None else []

def get_employees(limit = 100,offset = 0):
        response = requests.get('%s?limit=%s&offset=%s' % (current_app.config['EMPLOYEES_ENDPOINT'],limit,offset))
        response.raise_for_status()
        return response.json()
        
def get_managers(employees,level):
        ids = set([e["manager"] for e in employees if e["manager"] is not None])
        qs = '&id='.join(str(id) for id in list(ids))
        response = requests.get('%s?id=%s' % (current_app.config['EMPLOYEES_ENDPOINT'],qs))
        response.raise_for_status()
        data['managers'] = response.json()
        if(level > 1):
            for x in range(1, level):
                ids = set([e["manager"] for e in data['managers'] if e["manager"] is not None])
                qs = '&id='.join(str(id) for id in list(ids))
                response = requests.get('%s?id=%s' % (current_app.config['EMPLOYEES_ENDPOINT'],qs))
                response.raise_for_status()
                data['managers'] += response.json()
                

def get_employee_by_id(id):
    e = next((e for e in data['managers'] if int(e['id']) == id), None)
    if(e is None):
        response = requests.get('%s?id=%s' % (current_app.config['EMPLOYEES_ENDPOINT'],id))
        return response.json()[0]
    else:
        return e
def get_department_by_id(id):
    return next((d for d in data['departments'] if int(d['id']) == id), None)

def get_office_by_id(id):
    return next((o for o in data['offices'] if o['id'] == id), None)

def get_expanded(obj,expand):
    if(obj is None): return obj  
    expanded = expand.split('.')
    exObj = dotty(obj)
    attrs = []
    while len(expanded) > 0:
        ex = expanded.pop(0)
        attrs.append(ex) 
        if (isinstance(exObj['.'.join(attrs)], int)):
            exObj['.'.join(attrs)] = get_expand(exObj['.'.join(attrs)],ex,employees)
        else:
            break
    return exObj.to_dict()

def get_expand(id,ex,employees):
    if(ex == 'superdepartment'):
        exObj = get_department_by_id(id) 
    if(ex == 'department'):
        exObj = get_department_by_id(id)
    if(ex == 'manager'):
        exObj = get_employee_by_id(id)
        data['managers'].append(exObj)
    if(ex == 'office'):
        exObj = get_office_by_id(id)
    return exObj
    

@bp.route('/employees')
def employees():
    try:
        limit = request.args.get('limit') if request.args.get('limit') is not None else 100
        offset = request.args.get('offset')  if request.args.get('offset') is not None else 0
        if int(limit) > 1000:
            return jsonify({'Error': 'Max limit = 1000'})
        response = get_employees(limit,offset)
        employees = []
        if(len(data['expands']) == 0):
            employees = response
        else:
            exManager = next((ex for ex in data['expands'] if 'manager' in ex), None)
            if(exManager is not None):
                get_managers(response,len(exManager.split('.')))
            for e in response:
                for expand in data['expands']:   
                    e = get_expanded(e,expand) if expand is not None else e
                employees.append(e)  
    except KeyError as err:
        return jsonify({'Error': 'expand key does not exists: %s' % err}) 
    except Exception as err:
        print (err)
        return jsonify({'Error': 'an error ocurred'}) 
    else:

        return jsonify(employees) #jsonify(employees)

@bp.route('/employees/<int:id>')
def employee(id):
    try:
        d = get_employee_by_id(id)
        
        if(d is None):
            abort(404)
        for expand in data['expands']:  
            d = get_expanded(d,expand) if expand is not None else d
        
        return jsonify(d)

    except KeyError as err:
        print(err)
        return jsonify({'Error': 'expand key does not exists: %s' % err}) 
    except Exception as err:
        print(err)
        return jsonify({'Error': 'an error ocurred'})         


@bp.route('/departments')
def departments():
    try:
        limit = int(request.args.get('limit')) if request.args.get('limit') is not None else 100
        offset = int(request.args.get('offset'))  if request.args.get('offset') is not None else 0
        if int(limit) > 1000:
            return jsonify({'Error': 'Max limit = 1000'})
        
        
        departments = [];

        for d in data['departments'][offset:offset+limit]:
            for expand in data['expands']:   
                d = get_expanded(d,expand) if expand is not None else d
            departments.append(d)    
        

        return jsonify(departments)

    except KeyError as err:
        return jsonify({'Error': 'expand key does not exists: %s' % err}) 
    except Exception as err:
        return jsonify({'Error': 'an error ocurred'}) 

@bp.route('/departments/<int:id>')
def department(id):
    try:
        d = get_department_by_id(id)
        
        if(d is None):
            abort(404)
        for expand in data['expands']:    
                d = get_expanded(d,expand) if expand is not None else d
        
        return jsonify(d)

    except KeyError as err:
        return jsonify({'Error': 'expand key does not exists: %s' % err}) 
    except Exception as err:
        return jsonify({'Error': 'an error ocurred'})         

@bp.route('/offices')
def offices():
    try:
        limit = int(request.args.get('limit')) if request.args.get('limit') is not None else 100
        offset = int(request.args.get('offset'))  if request.args.get('offset') is not None else 0
        if int(limit) > 1000:
            return jsonify({'Error': 'Max limit = 1000'})
        
        return jsonify(data['offices'][offset:offset+limit])

    except Exception as err:
        print(err)
        return jsonify({'Error': 'an error ocurred'}) 

@bp.route('/offices/<int:id>')
def office(id):
    try:
        d = get_office_by_id(id)

        if(d is None):
            abort(404)
        
        return jsonify(d)

    except Exception as err:
        print(err)
        return jsonify({'Error': 'an error ocurred'})         


