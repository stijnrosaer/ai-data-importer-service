import json
import os
from string import Template

from flask import request, jsonify

from helpers import query, update, log, generate_uuid
from escape_helpers import sparql_escape_uri, sparql_escape_string, sparql_escape_int, sparql_escape_datetime
import pandas as pd

from .file_handler import postfile


def store_json(data):
    """
    Store json data to a file and call postfile to store in in a triplestore
    :param data: data in json format
    :return: response from storing data in triple store
    """
    file_id = generate_uuid()
    dumpFileName = f"{file_id}.json"
    dumpFilePath = f'/share/ai-files/{dumpFileName}'
    with open(dumpFilePath, 'w') as f:
        json.dump(data, f)

    resp = postfile(dumpFilePath, dumpFileName)
    return resp


@app.route("/data/query", methods=["GET"])
def query_data():
    """
    Endpoint for loading data from triple store using a query file and converting it to json
    Accepted request arguments:
        - filename: filename that contains the query
        - limit: limit the amount of data retrieved per query execution, allows for possible pagination
        - global_limit: total amount of items to be retrieved
    :return: response from storing data in triple store, contains virtual file id and uri
    """

    # env arguments to restrict option usage
    acceptFilename = os.environ.get('ACCEPT_FILENAME') or False
    acceptOptions = os.environ.get('ACCEPT_OPTIONS') or False

    # default filename
    filename = "/config/input.sparql"
    if acceptFilename:
        f = request.args.get("filename")
        if f:
            filename = "/config/" + f

    # default amount of items to retrieve per request
    limit = 1000
    globalLimit = float('inf')
    if acceptOptions:
        limit = int(request.args.get("limit") or 1000)
        globalLimit = float(request.args.get("global_limit") or float("inf"))

    if globalLimit < limit:
        limit = globalLimit

    # load query
    q = ""
    if os.path.isfile(filename):
        with open(filename) as f:
            q = f.read()
    else:
        return "Requested filename does not exist", 204

    # iteratively retrieve requested amount of data
    ret = {}
    if q:
        stop = False
        index = 0
        while not stop and (limit * index) <= globalLimit - 1:
            stop = True
            offset = limit * index

            formatted = (q + f" LIMIT {limit} OFFSET {offset}")
            resp = query(formatted)["results"]["bindings"]

            # convert data to json
            for val in resp:
                stop = False
                for k, v in val.items():
                    if k not in ret:
                        ret[k] = []
                    ret[k].append(v["value"])
            index += 1

    # store json data to file and in triple store
    storeResp = store_json(ret)

    return jsonify(storeResp)


@app.route("/data/file", methods=["GET"])
def file_data():
    """
        Endpoint for loading data from a csv file and converting it to json
        Accepted request arguments:
            - filename: filename that contains the data
            - columns: csv data columns to use
        :return: response from storing data in triple store, contains virtual file id and uri
        """

    # env arguments to restrict option usage
    acceptFilename = os.environ.get('ACCEPT_FILENAME') or False
    acceptOptions = os.environ.get('ACCEPT_OPTIONS') or False

    # default filename
    filename = "/share/input.csv"
    if acceptFilename:
        f = request.args.get("filename")
        if f:
            filename = "/share/" + f

    columns = None
    if acceptOptions:
        columns = request.args.get("columns") or None

    if not os.path.isfile(filename):
        return "Data inaccessible", 204

    data = pd.read_csv(filename).astype(str)

    # select requested columns, all if not specified
    if columns:
        columns = list(columns.split(","))
        dataColumns = list(data.columns)

        for col in columns:
            if col not in dataColumns:
                return f"Invalid column {col} requested", 204

        data = data[columns]

    ret = {}

    for col in data:
        ret[col] = data[col].tolist()

    # store json data to file and in triple store
    storeResp = store_json(ret)

    return jsonify(storeResp)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    Default endpoint/ catch all
    :param path: requested path
    :return: debug information
    """
    return 'You want path: %s' % path, 404


if __name__ == '__main__':
    debug = os.environ.get('MODE') == "development"
    app.run(debug=debug, host='0.0.0.0', port=80)
