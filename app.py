from flask import Flask, render_template, request, jsonify, Response
import json, datetime
from bson import json_util
from bson.objectid import ObjectId
from pymongo import Connection
from flask_mime import Mime
from cors import crossdomain

app = Flask(__name__)
mimetype = Mime(app)
connection = Connection('localhost', 27017)
db = connection.foo

def toJson(data):
    return json.dumps(data, default=json_util.default)

@app.route('/api/people', methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin='*')
def people():
    if request.method == 'GET':
        results = db['people'].find()
        json_results = []
        for result in results:
            json_results.append(result)
        return Response(toJson(json_results), status=200, mimetype='application/json')
    
    if request.method == 'POST':
        js = request.json
        netid = js['data']['attributes']['netid']
        res = db['people'].find_one({"data.attributes.netid": netid })
        if res == None:
            res = db['people'].insert(js)
            return Response(toJson(res), status=200, mimetype='application/json')
        else:
            return Response(json.dumps({"error": "person already exists"}), status=400, mimetype='application/json')
    else:
        return Response(json.dumps({"error": "NOT FOUND"}), status=404, mimetype='application/json')


@app.route('/api/people/<person_id>', methods=['GET', 'PATCH', 'OPTIONS'])
def person(person_id):
    if request.method == 'GET':
        result = db['people'].find_one({'_id': ObjectId(person_id)})
        return Response(toJson(result), status=200, mimetype='application/json')
    if request.method == 'PATCH':
        js = request.json
        result = db['people'].find_one({'_id': ObjectId(person_id)})
        if result == None:
            return Response(json.dumps({"error": "person_id doesn't exist"}), status=400, mimetype='application/json')
        else:
            result = toJson(result)
            # add attributes
            try:
                attributes = js['data']['attributes']
                name = attributes.get('name', None)
                nNumber = attributes.get('nNumber', None)
                netid = attributes.get('netid', None)
                password = attributes.get('password', None)
                if name != None: db.people.update({"_id": ObjectId(person_id)}, {"$set": { "data.attributes.name": name }})
                if nNumber != None: db.people.update({"_id": ObjectId(person_id)}, {"$set": { "data.attributes.nNumber": nNumber }})
                if netid != None: db.people.update({"_id": ObjectId(person_id)}, {"$set": { "data.attributes.netid": netid }})
                if password != None: db.people.update({"_id": ObjectId(person_id)}, {"$set": { "data.attributes.password": password }})
                return Response(json.dumps({}), status=400, mimetype='application/json')
            except KeyError:
                return Response(json.dumps({"error": "json format not accurate"}), status=400, mimetype='application/json')
            # add links
    else:
        return Response(json.dumps({"error": "NOT FOUND"}), status=404, mimetype='application/json')

@app.route('/api/sell_posts', methods=['GET', 'POST', 'OPTIONS'])
def sell_posts():
    if request.method == 'GET':
        results = db['sell_posts'].find()
        json_results = []
        for result in results:
            json_results.append(result)
        return Response(toJson(json_results), status=200, mimetype='application/json')
    
    if request.method == 'POST':
        js = request.json
        seller_id = js['links']['seller']['_id']
        res = db['people'].find_one({"_id": ObjectId(seller_id)})
        if res == None:
            return Response(json.dumps({"error": "seller_id does not exist"}), status=404, mimetype='application/json')
        else:
            offset = js['data']['attributes']['days_until_expiration']
            now = datetime.datetime.now()
            diff = datetime.timedelta(days=offset)
            expired_by = now + diff
            js['data']['attributes']['expired_by'] = expired_by
            if js['data']['attributes']['price'] != None and js['data']['attributes']['expired_by'] != None and len(js['data']['attributes']['locations']) > 0 and js['data']['type'] == 'sell_posts':
                res = db['sell_posts'].insert(js)
                post_id = json.loads(toJson(res))['$oid']
                if post_id != None:
                    db.people.update({"_id": ObjectId(seller_id)}, {"$push": { "links.sell_posts": { "_id": post_id } }})
                return Response(toJson(res), status=200, mimetype='application/json')
            else:
                return Response(json.dumps({"error": "missing required info"}), status=404, mimetype='application/json')
    else:
        return Response(json.dumps({"error": "NOT FOUND"}), status=404, mimetype='application/json')

@app.route('/api/sell_posts/<post_id>', methods=['GET', 'DELETE'])
def sell_post(post_id):
    if request.method == 'GET':
        result = db['sell_posts'].find_one({'_id': ObjectId(post_id)})
        return Response(toJson(result), status=200, mimetype='application/json')
    if request.method == 'DELETE':
        result = db['sell_posts'].remove({'_id': ObjectId(post_id)})
        return Response(toJson(result), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"error": "NOT FOUND"}), status=404, mimetype='application/json')


@app.route('/api/buy_posts', methods=['GET', 'POST', 'OPTIONS'])
def buy_posts():
    if request.method == 'GET':
        results = db['buy_posts'].find()
        json_results = []
        for result in results:
            json_results.append(result)
        return toJson(json_results)
    
    if request.method == 'POST':
        js = request.json
        buyer_id = js['links']['buyer']['_id']
        res = db['people'].find_one({"_id": ObjectId(buyer_id)})
        if res == None:
            return Response(json.dumps({"error": "buyer_id does not exist"}), status=404, mimetype='application/json')
        else:
            offset = js['data']['attributes']['days_until_expiration']
            now = datetime.datetime.now()
            diff = datetime.timedelta(days=offset)
            expired_by = now + diff
            js['data']['attributes']['expired_by'] = expired_by
            print js['data']['type']
            if js['data']['attributes']['price'] != None and js['data']['attributes']['expired_by'] != None and len(js['data']['attributes']['locations']) > 0 and js['data']['type'] == 'buy_posts':
                res = db['buy_posts'].insert(js)
                post_id = json.loads(toJson(res))['$oid']
                if post_id != None:
                    db.people.update({"_id": ObjectId(buyer_id)}, {"$push": { "links.buy_posts": { "_id": post_id } }})
                return Response(toJson(res), status=200, mimetype='application/json')
            else:
                return Response(json.dumps({"error": "missing required info"}), status=404, mimetype='application/json')
    else:
        return Response(json.dumps({"error": "NOT FOUND"}), status=404, mimetype='application/json')

@app.route('/api/buy_posts/<post_id>', methods=['GET'])
def buy_post(post_id):
    if request.method == 'GET':
        result = db['buy_posts'].find_one({'_id': ObjectId(post_id)})
        return Response(toJson(result), status=200, mimetype='application/json')
    if request.method == 'DELETE':
        result = db['buy_posts'].remove({'_id': ObjectId(post_id)})
        return Response(toJson(result), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"error": "NOT FOUND"}), status=404, mimetype='application/json')

if __name__ == '__main__':
    app.debug = True
    app.run()
