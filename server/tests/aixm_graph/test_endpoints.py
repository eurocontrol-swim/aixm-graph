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

import json
import os
from unittest import mock
from unittest.mock import Mock

import pytest
from werkzeug.datastructures import FileStorage

from aixm_graph.datasets.datasets import AIXMDataSet
from aixm_graph.datasets.features import AIXMFeature, Feature
from aixm_graph.datasets.fields import Field
from aixm_graph.graph import Graph


@mock.patch('aixm_graph.cache.get_datasets')
def test_get_datasets(mock_get_datasets, test_client):
    dataset = Mock()
    dataset.name = 'some name'
    dataset.id = 'some id'
    mock_get_datasets.return_value = [dataset]

    response = test_client.get('/api/datasets')
    assert response.status_code == 200

    response_data = json.loads(response.data)['data']
    assert response_data[0]['dataset_id'] == 'some id'
    assert response_data[0]['dataset_name'] == 'some name'


def test_get_dataset_feature_types__dataset_not_found__404(test_client):
    response = test_client.get('/api/datasets/some_id/feature_types')
    assert response.status_code == 404

    response_data = json.loads(response.data)
    assert response_data['error'] == 'Dataset with id some_id does not exist'


@mock.patch('aixm_graph.cache.get_dataset_by_id')
def test_get_dataset_feature_types__process_fails__500(mock_get_dataset_by_id, test_client):
    dataset = AIXMDataSet('filepath')
    dataset.process = Mock(side_effect=Exception('process error'))

    mock_get_dataset_by_id.return_value = dataset

    response = test_client.get('/api/datasets/some_id/feature_types')
    assert response.status_code == 500

    response_data = json.loads(response.data)
    assert response_data['error'] == 'process error'


@pytest.mark.parametrize('feature_type_stats, expected_feature_types', [
    (
        {
            'feature1': {
                'size': 10,
                'features_num_with_broken_xlinks': 1
            },
            'feature2': {
                'size': 20,
                'features_num_with_broken_xlinks': 0
            }
        },
        [
            {
                'name':'feature1',
                'size': 10,
                'features_num_with_broken_xlinks': 1
            },
            {
                'name': 'feature2',
                'size': 20,
                'features_num_with_broken_xlinks': 0
            }
        ]
    )
])
@mock.patch('aixm_graph.cache.get_dataset_by_id')
def test_get_dataset_feature_types__returns_feature_types__200(
        mock_get_dataset_by_id, test_client, feature_type_stats, expected_feature_types):
    dataset = AIXMDataSet('filepath')
    dataset.process = Mock(return_value=dataset)
    dataset._feature_type_stats = feature_type_stats

    mock_get_dataset_by_id.return_value = dataset

    response = test_client.get('/api/datasets/some_id/feature_types')
    assert response.status_code == 200

    response_data = json.loads(response.data)['data']

    assert expected_feature_types == response_data['feature_types']


def test_get_graph_for_feature_type__dataset_not_found__404(test_client):
    response = test_client.get('/api/datasets/some_id/feature_types/some_type_name/graph')
    assert response.status_code == 404

    response_data = json.loads(response.data)
    assert response_data['error'] == 'Dataset with id some_id does not exist'

    dataset = AIXMDataSet('filepath')
    dataset.id = 'some_id'


@mock.patch('aixm_graph.cache.get_dataset_by_id')
def test_get_graph_for_feature_type__feature_type_not_found__404(mock_get_dataset_by_id, test_client):
    dataset = AIXMDataSet('filepath')
    dataset.id = 'some_id'
    mock_get_dataset_by_id.return_value = dataset

    response = test_client.get('/api/datasets/some_id/feature_types/some_type_name/graph')
    assert response.status_code == 404

    response_data = json.loads(response.data)
    assert response_data['error'] == 'Dataset has not feature type with name some_type_name'


@mock.patch('aixm_graph.cache.get_dataset_by_id')
def test_get_graph_for_feature_type__no_errors__200(mock_get_dataset_by_id, test_client):
    dataset = AIXMDataSet('filepath')
    graph = Graph()
    dataset.id = 'some_id'
    dataset._features_dict = {'1': AIXMFeature('TestFeature1'), '2': AIXMFeature('TestFeature2')}
    dataset.get_graph = Mock(return_value=graph)

    mock_get_dataset_by_id.return_value = dataset

    path = '/api/datasets/some_id/feature_types/TestFeature1/graph?offset=0&limit=5'

    response = test_client.get(path)
    assert response.status_code == 200

    response_data = json.loads(response.data)['data']
    assert response_data['offset'] == 0
    assert response_data['limit'] == 5
    assert response_data['size'] == 1
    assert response_data['graph'] == graph.to_json()
    assert response_data['next_offset'] is None
    assert response_data['prev_offset'] is None


@pytest.mark.parametrize('field_value, query, extected_results_size', [
    ('some_value', 'some', 1),
    ('some_value', 'ome', 1),
    ('some_value', 'some-', 0),
    ('some_value', 'val', 1),
    ('some_value', 'vale', 0),
])
@mock.patch('aixm_graph.cache.get_dataset_by_id')
def test_get_graph_for_feature_type__with_filter__200(
        mock_get_dataset_by_id, test_client, field_value, query, extected_results_size):
    graph = Graph()

    feature1 = AIXMFeature('TestFeature1')
    feature1_time_slice1 = Feature(name='timeSlice')
    feature1_time_slice1.data_fields.append(Field(name='field', text=field_value))
    feature1.time_slices['ts_version_1'] = feature1_time_slice1

    dataset = AIXMDataSet('filepath')
    dataset.id = 'some_id'
    dataset._features_dict = {'feature1_id': feature1, 'feature2_id': AIXMFeature('TestFeature2')}
    dataset.get_graph = Mock(return_value=graph)

    mock_get_dataset_by_id.return_value = dataset

    path = f'/api/datasets/some_id/feature_types/TestFeature1/graph?offset=0&limit=5&key={query}'

    response = test_client.get(path)
    assert response.status_code == 200

    response_data = json.loads(response.data)['data']
    assert response_data['offset'] == 0
    assert response_data['limit'] == 5
    assert response_data['size'] == extected_results_size
    assert response_data['graph'] == graph.to_json()
    assert response_data['next_offset'] is None
    assert response_data['prev_offset'] is None


def test_get_graph_for_feature__dataset_not_found__404(test_client):
    response = test_client.get('/api/datasets/some_id/features/some_id/graph')
    assert response.status_code == 404

    response_data = json.loads(response.data)
    assert response_data['error'] == 'Dataset with id some_id does not exist'

    dataset = AIXMDataSet('filepath')
    dataset.id = 'some_id'


@mock.patch('aixm_graph.cache.get_dataset_by_id')
def test_get_graph_for_feature__feature_not_found__404(mock_get_dataset_by_id, test_client):
    dataset = AIXMDataSet('filepath')
    dataset.id = 'some_id'
    mock_get_dataset_by_id.return_value = dataset

    response = test_client.get('/api/datasets/some_id/features/some_id/graph')
    assert response.status_code == 404

    response_data = json.loads(response.data)
    assert response_data['error'] == 'Feature with id some_id does not exist'


@mock.patch('aixm_graph.cache.get_dataset_by_id')
def test_get_graph_for_feature__no_errors__200(mock_get_dataset_by_id, test_client):
    dataset = AIXMDataSet('filepath')
    graph = Graph()
    dataset.id = 'some_id'
    dataset._features_dict = {'1': AIXMFeature('TestFeature1'), '2': AIXMFeature('TestFeature2')}
    dataset.get_graph_for_feature = Mock(return_value=graph)

    mock_get_dataset_by_id.return_value = dataset

    path = '/api/datasets/some_id/features/1/graph'

    response = test_client.get(path)
    assert response.status_code == 200

    response_data = json.loads(response.data)['data']
    assert response_data['graph'] == graph.to_json()


def test_upload_aixm__no_file_part__returns_400(test_client):
    response = test_client.post('/api/upload', data={})
    assert response.status_code == 400

    response_data = json.loads(response.data)
    assert response_data['error'] == 'No file part'


def test_upload_aixm__no_selected_file__returns_400(test_client):
    file = FileStorage()
    file.filename = ''

    response = test_client.post('/api/upload', data={'file': file})
    assert response.status_code == 400

    response_data = json.loads(response.data)
    assert response_data['error'] == 'No selected file'


def test_upload_aixm__not_allowed_file__returns_400(test_client):
    file = FileStorage()
    file.filename = 'filename.invalid_ext'

    response = test_client.post('/api/upload', data={'file': file})
    assert response.status_code == 400

    response_data = json.loads(response.data)
    assert response_data['error'] == 'File is not allowed'


@mock.patch('aixm_graph.cache.get_dataset_by_name')
def test_upload_aixm__dataset_already_exists__returns_400(mock_get_dataset_by_name, test_client):
    file = FileStorage()
    file.filename = 'filename.xml'
    mock_get_dataset_by_name.return_value = AIXMDataSet(file.filename)

    response = test_client.post('/api/upload', data={'file': file})
    assert response.status_code == 400

    response_data = json.loads(response.data)
    assert response_data['error'] == 'Dataset already exists'


@mock.patch('aixm_graph.utils.validate_file_form')
def test_upload_aixm__file_is_uploaded__returns_201(mock_validate_file_form, test_app, test_client):
    file = FileStorage()
    file.filename = 'filename.xml'
    file.save = Mock()

    expected_final_filepath = os.path.join(test_app.config['UPLOAD_FOLDER'], file.filename)

    mock_validate_file_form.return_value = file

    response = test_client.post('/api/upload', data={'file': None})
    assert response.status_code == 201

    response_data = json.loads(response.data)['data']
    assert response_data['dataset_name'] == file.filename

    file.save.assert_called_once_with(expected_final_filepath)
