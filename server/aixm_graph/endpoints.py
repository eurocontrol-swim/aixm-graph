"""
Copyright 2020 EUROCONTROL
==========================================

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions
   and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
   and the following disclaimer in the documentation and/or other materials provided with the
   distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse
   or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

==========================================

Editorial note: this license is an instance of the BSD license template as provided by the Open
Source Initiative: http://opensource.org/licenses/BSD-3-Clause

Details on EUROCONTROL: http://www.eurocontrol.int
"""

__author__ = "EUROCONTROL (SWIM)"

import logging
import os
from functools import wraps
from itertools import tee
from typing import Callable, TypeVar, Tuple, Any, Dict, Union, List

from flask import Blueprint
from flask import request, current_app as app, send_file
from werkzeug.utils import secure_filename

from aixm_graph import cache
from aixm_graph.errors import APIError, NotFoundError, BadRequestError
from aixm_graph import utils

_logger = logging.getLogger(__name__)

ResponseType = Tuple[Union[List[Dict[str, Any]], Dict[str, Any]], int]

aixm_graph_blueprint = Blueprint('aixm_graph', __name__, url_prefix='/api')


def handle_response(f) -> Callable:
    """
    :param f:
    :return:
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        result = {}
        try:
            result['data'], status_code = f(*args, **kwargs)
        except APIError as e:
            _logger.error(str(e))
            result['error'] = e.description
            status_code = e.status_code
        except Exception as e:
            _logger.exception(str(e))
            result['error'] = str(e)
            status_code = 500

        return result, status_code
    return decorator


@aixm_graph_blueprint.route('/datasets', methods=['GET'])
@handle_response
def get_datasets() -> ResponseType:
    """
    Retrieves and the returns the id and name of all available datasets
    :return:
    """
    datasets = cache.get_datasets()

    return [
       {
           "dataset_name": dataset.name,
           "dataset_id": dataset.id
       }
       for dataset in datasets
    ], 200


@aixm_graph_blueprint.route('/datasets/<dataset_id>/feature_types', methods=['GET'])
@handle_response
def get_dataset_feature_types(dataset_id: str) -> ResponseType:
    """
    Retrieves info for the available feature types of the dataset i.e. name, how many features
    it has and how many of them have broken xlink references.
    :param dataset_id:
    :return:
    """
    dataset = cache.get_dataset_by_id(dataset_id)

    if dataset is None:
        raise NotFoundError(f'Dataset with id {dataset_id} does not exist')

    if not dataset.feature_type_stats:
        dataset.process()

    feature_types = [
        {
            'name': feature_type_name,
            'size': stats['size'],
            'features_num_with_broken_xlinks': stats['features_num_with_broken_xlinks']
        }
        for feature_type_name, stats in dataset.feature_type_stats.items()
    ]
    feature_types = sorted(feature_types, key=lambda k: k['name'])

    return {
        "feature_types": feature_types
    }, 200


@aixm_graph_blueprint.route(
    '/datasets/<dataset_id>/feature_types/<feature_type_name>/graph', methods=['GET'])
@handle_response
def get_graph_for_feature_type(dataset_id: str, feature_type_name: str) -> ResponseType:
    """
    Generates the graph for a specific feature type paginated based on the offset and limit provided
    in the URL query.

    :param dataset_id:
    :param feature_type_name:
    :return:
    """
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', app.config['PAGE_LIMIT']))
    field_value = request.args.get('key')

    dataset = cache.get_dataset_by_id(dataset_id)

    if dataset is None:
        raise NotFoundError(f'Dataset with id {dataset_id} does not exist')

    if not dataset.has_feature_type_name(feature_type_name):
        raise NotFoundError(f'Dataset has not feature type with name {feature_type_name}')

    # filter features returns a generator and we need it twice here, hence the use of tee
    features, _features = tee(dataset.filter_features(name=feature_type_name,
                                                      field_value=field_value))

    graph = dataset.get_graph(features=features, offset=offset, limit=limit + offset)

    size = sum(1 for _ in _features)

    return {
        'offset': offset,
        'limit': limit,
        'size': size,
        'graph': graph.to_json(),
        'next_offset': utils.get_next_offset(offset, limit, size),
        'prev_offset': utils.get_prev_offset(offset, limit),
    }, 200


@aixm_graph_blueprint.route('/datasets/<dataset_id>/features/<feature_id>/graph', methods=['GET'])
@handle_response
def get_graph_for_feature(dataset_id: str, feature_id: str) -> ResponseType:
    """
    Generates the graph for a specific feature of the dataset

    :param dataset_id:
    :param feature_id:
    :return:
    """
    dataset = cache.get_dataset_by_id(dataset_id)

    if dataset is None:
        raise NotFoundError(f'Dataset with id {dataset_id} does not exist')

    feature = dataset.get_feature_by_id(feature_id)

    if feature is None:
        raise NotFoundError(f'Feature with id {feature_id} does not exist')

    graph = dataset.get_graph_for_feature(feature=feature)

    return {
        'graph': graph.to_json()
    }, 200


@aixm_graph_blueprint.route('/upload', methods=['POST'])
@handle_response
def upload_aixm_dataset() -> ResponseType:
    """
    Uploads a dataset after applying some validation.
    The max size of the file is handled by nginx.

    :return:
    """
    try:
        file = utils.validate_file_form(request.files)
    except ValueError as e:
        raise BadRequestError(description=str(e))

    if cache.get_dataset_by_name(file.filename) is not None:
        raise BadRequestError('Dataset already exists')

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    dataset = cache.create_dataset(filepath)

    return {
        'dataset_name': dataset.name,
        'dataset_id': dataset.id
    }, 201


@aixm_graph_blueprint.route('/datasets/<dataset_id>/download', methods=['GET'])
def download_skeleton(dataset_id: str):
    """
    Returns the generated skeleton of the dataset as an attachment in the response so it can be
    downloaded as a file in the browser.

    :param dataset_id:
    :return:
    """
    dataset = cache.get_dataset_by_id(dataset_id)

    skeleton_filepath = dataset.generate_skeleton()

    return send_file(skeleton_filepath, as_attachment=True), 200
