from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import logging
import bcrypt
import uuid
import os
import requests
from datetime import datetime
from DBManager import DBManager


application = Flask(__name__)
CORS(application, resources=r'/*')
db = DBManager()
region = 'us-east-1'

application.config["JWT_SECRET_KEY"] = "Scalable Cloud Programming"
jwt = JWTManager(application)

@application.route("/login", methods=["POST"])
def login():
    post_data = request.get_json()
    email = post_data.get("email")
    password = post_data.get("password").encode('utf-8')
    
    fe = Key('email').eq(email)
    
    try:
        user = db.scan(
            region=region,
            table_name='users',
            filter_expression=fe
            )['Items'][0] # as it will return only one result
    except IndexError: # it means email is incorrect
        user = None
    
    if user is None:
        return jsonify({"msg": "Incorrect login credentials"}), 401
    else:
        if not bcrypt.checkpw(password, bytes(user['password'])):
            return jsonify({"msg": "Incorrect login credentials"}), 401
        
    access_token = create_access_token(identity=user['id'])
    
    return jsonify(access_token=access_token)

@application.route("/me", methods=["GET"])
@jwt_required()
def getMe():
    id = get_jwt_identity()
    key_schema = {'id': id}
    
    item = db.get_an_item(region, 'users', key_schema)
    
    user = {
        'id': item['id'],
        'fullName': item['fullName'],
        'age': int(item['age']),
        'gender': int(item['gender']),
        'mobile': item['mobile'],
        'username': item['username'],
        'email': item['email'],
    }
    
    return user, 200

@application.route("/updateMe", methods=["POST"])
@jwt_required()
def updateMe():
    post_data = request.get_json()
    name = post_data.get("fullName")
    age = post_data.get("age")
    gender = post_data.get("gender")
    mobile = post_data.get("mobile")
    username = post_data.get("username")
    id = get_jwt_identity()
    key_info = {
        'id': id
    }
    success = True
    try:
        response = db.update_item(
           table_name='users',
           region=region,
           key=key_info,
           updateExpression='SET fullName = :fullName, age = :age, gender = :gender, mobile = :mobile, username = :username', 
           expressionAttributes={
               ':fullName': name,
               ':age': age,
               ':gender': gender,
               ':mobile': mobile,
               ':username': username,
            }
        )
    except (ClientError, KeyError) as e:
        logging.error(e)
        success = False

    return {'success': success}, 200

@application.route("/availability", methods=["GET"])
@jwt_required()
def getAvailability():
    id = get_jwt_identity()
    fe = Key('user_id').eq(id)
    
    availability = db.scan(region=region,
                           table_name='availabilities',
                           filter_expression=fe)['Items']
                           
    return jsonify(availability), 200

@application.route("/availability/create", methods=["POST"])
@jwt_required()
def createAvailability():
    id = get_jwt_identity()
    post_data = request.get_json()
    
    new_availability = {
        'id': str(uuid.uuid1()),
        'created_at': str(datetime.now()),
        'user_id': id,
        'dayOfWeek': post_data['dayOfWeek'],
        'fromTime': post_data['fromTime'],
        'toTime': post_data['toTime']
    }
    dayOfWeek = post_data['dayOfWeek']
    fromTime = post_data['fromTime']
    toTime = post_data['toTime']
    
    db.store_an_item(region, 'availabilities', new_availability)
    return {'status': 'success'}, 200

@application.route("/availability/update/<id>", methods=["POST"])
@jwt_required()
def updateAvailability(id):
    post_data = request.get_json()
    key = {'id': id}
    
    metrics = post_data['metrics']
    
    update_expression = 'SET'
    expression_attributes = {}
    # build update expression and expression attribute values based on the request
    for index,metric in enumerate(metrics):
        update_expression += ' {} = :{}'.format(metric['field_name'],metric['field_name'])
        if index != len(metrics) - 1:
            update_expression += ','
        expression_attributes[':{}'.format(metric['field_name'])] = {metric['type']: metric['value']}
    
    response = db.update_item(table_name='availabilities', 
                             region=region,
                             key=key,
                             updateExpression=update_expression,
                             expressionAttributes=expression_attributes
                        )
    updated_item = response.get('Attributes', {})
    return jsonify(updated_item), 200

@application.route("/availability/delete/<id>", methods=["POST"])
@jwt_required()
def deleteAvailability(id):
    key = {'id': {
            'S': id
            }
        }
    success = True
    try:
        response = db.delete_item(region=region,
                   table_name='availabilities',
                   key=key
        )
    except (ClientError, KeyError) as e: 
        logging.error(e)
        success = False
    
    return {'success': success}, 200


@application.route("/delivery", methods=["GET"])
@jwt_required()
def getDeliveries():
    id = get_jwt_identity()
    fe = Key('rider_id').eq(id)
    
    deliveries = db.scan(table_name='deliveries',
                         region=region, 
                         filter_expression=fe)['Items']
    
    return jsonify(deliveries), 200

@application.route("/delivery/create", methods=["POST"])
def createDeliveryRequest():
    post_data = request.get_json()
    delivery = {
        'id': str(uuid.uuid1()),
        'created_at': str(datetime.now()),
        'delivery_status': 'Received',
        'origin': post_data['origin'],
        'destination': post_data['destination'],
        'order_nr': post_data['order_nr'],
        'weight': post_data['weight'],
        'dimensions': post_data['dimensions'],
        'type': post_data['type'],
        'customer_info': post_data['customer_info'],
        'rider_id': post_data['rider_id'],
        'comment': post_data['comment']
    }
    
    db.store_an_item(item=delivery,
                     region=region,
                     table_name='deliveries'
                )
    
    return jsonify(delivery), 200

@application.route("/delivery/<id>", methods=["POST"])
@jwt_required()
def updateDeliveryStatus(id):
    post_data = request.get_json()
    key_info = {
        'id': id
    }
    
    response = db.update_item(
       table_name='deliveries',
       region=region,
       key=key_info,
       updateExpression='SET delivery_status = :status', 
       expressionAttributes={
           ':status': post_data['delivery_status'],
        }
    )
    new_delivery = response['Attributes']
    # update requesting app:
    params = {'orderNumber': new_delivery['order_nr'],
               'updatedAttributes': {
                  'orderStatus': new_delivery['delivery_status'] 
                },
              }
    url = 'https://bc096ti86i.execute-api.us-east-1.amazonaws.com/Prod/orders'
    response = requests.post(url, json=params)
    
    return jsonify(new_delivery), 200
    
    
if __name__ == '__main__':
    application.run()