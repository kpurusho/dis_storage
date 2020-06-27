from flask import Flask, request, session, send_file
import coreapp
import config
import os
import shutil
import hashlib
import loadbalancer
import nodetracker
import fileop
import io
import json

app = Flask(__name__)
app.secret_key='disstorage'

@app.route('/files', methods=['PUT'])
def upload_file() -> str:
    filestream = request.files['file']
    store = getmetadatastore()
    app = create_core_app(store)
    app.setup()
    id = str(app.upload_content(filestream.filename, filestream))
    savemetadatastore(app.metadataStore)
    return id

@app.route('/files/<id>', methods=['DELETE'])
def delete_file(id):
    store = getmetadatastore()
    app = create_core_app(store)
    app.delete(id)
    savemetadatastore(app.metadataStore)
    return 'file deleted successfully'

@app.route('/files/<id>', methods=['GET'])
def get_file(id):
    store = getmetadatastore()
    app = create_core_app(store)
    (filename, content) = app.download(id)
    return send_file(io.BytesIO(content), as_attachment=True, attachment_filename=filename)


@app.route('/files/list', methods=['GET'])
def get_filelist():
    store = getmetadatastore()
    app = create_core_app(store)
    return json.dumps(app.getlist())


def create_core_app(store) -> coreapp.CoreApp:
    conf = config.Config(redundancyCount=1)
    nt = nodetracker.NodeTracker(conf)
    fop = fileop.FileOp(nt)
    lb = loadbalancer.RoundRobinLoadBalancer(conf, nt)
    app = coreapp.CoreApp(conf, lb, fop, store)
    return app

def getmetadatastore() -> dict:
    result = {}
    if os.path.exists('metadata.json'):
        with open('metadata.json', mode='r') as mf:
            return json.load(mf)
    
    return result

def savemetadatastore(store) -> None:
    with open('metadata.json', mode='w') as mf:
        mf.write(json.dumps(store))

if __name__ == '__main__':
    app.run(debug=True)