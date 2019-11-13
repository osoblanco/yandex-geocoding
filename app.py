from yandex_locator import *
from yandex_locator import geocode_enricher
from flask import Flask, request
import json

application = Flask(__name__)
application.secret_key = 'RandomKey'

@application.route('/yandex_locator', methods=['GET'])
def csv_upload():
    location = request.args.get('location')

    # given_name = ''
    # given_name = request.args.get('full_name')
    # if not given_name:
    #     given_name = "No Given Name"
    #
    # phero_meta_id = ''
    # phero_meta_id = request.args.get('phero_meta_id')
    #
    # if not phero_meta_id:
    #     phero_meta_id = "No Hero ID Given"

    full_scheme = geocode_enricher(location)

    json_dict = json.dumps(full_scheme)

    if not json_dict:
        return "Cant get data",404
    return json_dict

if __name__ == "__main__":
    application.run(host='0.0.0.0',port=5008, debug=False)
