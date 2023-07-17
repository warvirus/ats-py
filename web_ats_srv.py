####

from http import HTTPStatus
from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

@app.route('/')
def default():
    return 'hello world !'

data = {
    "age": 14,
    "money": 100000
}

@app.route('/get', methods=['GET'])
def get():
    return jsonify({"data": data, "status": HTTPStatus.OK})

@app.route('/post', methods=['POST'])
def post():
    params = request.get_json()
    print(params)
    params['username']

    return jsonify({"data": params, "status": HTTPStatus.OK})

@app.route('/hoga', methods=['POST'])
def set_hoga():
    params = request.get_json()
    print(params)
    # params['username']

    return jsonify({"data": params, "status": HTTPStatus.OK})

if __name__ == '__main__':
    app.run(port=8080, debug=True)