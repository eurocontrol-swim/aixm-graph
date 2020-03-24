"""
Copyright 2020 EUROCONTROL
==========================================

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
   disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

==========================================

Editorial note: this license is an instance of the BSD license template as provided by the Open Source Initiative:
http://opensource.org/licenses/BSD-3-Clause

Details on EUROCONTROL: http://www.eurocontrol.int
"""

__author__ = "EUROCONTROL (SWIM)"

import logging
import os
from functools import wraps
from itertools import tee
from typing import Dict

from flask import Blueprint, send_from_directory, request, current_app as app, send_file
from werkzeug.utils import secure_filename

from aixm_graph import cache
from aixm_graph.graph import get_file_feature_graph, get_file_features_graph
from aixm_graph.parser import process_aixm, generate_aixm_skeleton
from aixm_graph.stats import get_file_stats


_logger = logging.getLogger(__name__)

aixm_blueprint = Blueprint('aixm_graph',
                           __name__,
                           template_folder='templates',
                           static_folder='static')

########
# STATIC
########


@aixm_blueprint.route("/")
def index():
    return send_from_directory('web_app/templates/', "index.html")


@aixm_blueprint.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('web_app/static/js', path)


@aixm_blueprint.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('web_app/static/css', path)


@aixm_blueprint.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('web_app/static/img', path)


@aixm_blueprint.route('/favicon.ico')
def favicon():
    return send_from_directory('web_app/static/img', 'favicon.png', mimetype='image/png')


########
# API
########

def handle_response(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        status_code = 200
        result = {}
        try:
            result['data'] = f(*args, **kwargs)
        except Exception as e:
            _logger.exception(str(e))
            result['error'] = str(e)
            status_code = 400

        return result, status_code
    return decorator


@aixm_blueprint.route('/load-config', methods=['GET'])
@handle_response
def load_config():
    return cache.get_features_config()


@aixm_blueprint.route('/files/<file_id>/process', methods=['PUT'])
@handle_response
def process_file(file_id: str):
    file = cache.get_file(file_id)

    if not file['features']:
        process_aixm(file_id=file_id, features_config=cache.get_features_config())

    stats = file['stats']
    if not stats:
        stats = get_file_stats(file_id)
        cache.save_file_stats(file_id, stats)

    features_details = [
        {
            'name': key,
            'total_count': value['total_count'],
            'has_broken_xlinks': value['has_broken_xlinks']
        }
        for key, value in stats.items() if value['total_count'] > 0
    ]

    return {
        "features_details": features_details,
        "total_count": sum(s['total_count'] for s in features_details)
    }


@aixm_blueprint.route('/files/<file_id>/features/graph', methods=['GET'])
@handle_response
def get_graph_for_feature_name(file_id: str):
    name = request.args.get('name')
    if not name:
        raise ValueError("Feature name not specified")

    offset = int(request.args.get('offset', "0"))
    filter_key = request.args.get('key')

    limit = app.config['PAGE_LIMIT']
    # the features generator will be used twice
    features, features_ = tee(cache.filter_file_features(file_id=file_id, name=name, key=filter_key))

    graph = get_file_features_graph(file_id, features=features, offset=offset, limit=(limit + offset) - 1)

    return {
        'offset': offset,
        'limit': limit,
        'total_count': sum(1 for _ in features_),
        'graph': graph.to_json(),
    }


@aixm_blueprint.route('/files/<file_id>/features/<uuid>/graph', methods=['GET'])
@handle_response
def get_graph_for_feature_uuid(file_id: str, uuid: str):
    graph = get_file_feature_graph(file_id=file_id, feature_id=uuid)

    return {
        'graph': graph.to_json()
    }


@aixm_blueprint.route('/upload', methods=['POST'])
@handle_response
def upload_aixm():
    file = validate_file_form(request.files)

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    file_id = cache.save_file(filepath)

    return {
        'filename': filename,
        'file_id': file_id
    }


@aixm_blueprint.route('/files/<file_id>/download', methods=['GET'])
def download(file_id: str):
    skeleton_filepath = generate_aixm_skeleton(file_id=file_id, features=cache.get_file_features_gen(file_id))

    return send_file(skeleton_filepath, as_attachment=True)


def validate_file_form(file_form: Dict):
    if 'file' not in file_form:
        raise ValueError('No file part')

    file = file_form['file']
    if file.filename == '':
        raise ValueError('No selected file')

    if not allowed_file(file.filename):
        raise ValueError('File is not allowed')

    return file


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'xml'
