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
import logging.config
import os

from flask import Flask
from flask_cors import CORS
from pkg_resources import resource_filename

from aixm_graph import cache
from aixm_graph.datasets.datasets import AIXMDataSet
from aixm_graph.datasets.features import AIXMFeatureClassRegistry
from aixm_graph.utils import load_config
from aixm_graph.endpoints import aixm_blueprint

__author__ = "EUROCONTROL (SWIM)"


def create_app(config_file: str) -> Flask:
    app = Flask(__name__)

    app.register_blueprint(aixm_blueprint)
    app_config = load_config(filename=config_file)
    app.config.update(app_config)

    logging.config.dictConfig(app.config['LOGGING'])
    # enable CORS

    CORS(app, resources={r'/*': {'origins': '*'}})
    # generate classes per feature as they're found in the config file

    AIXMFeatureClassRegistry.load_feature_classes(app.config['FEATURES'])

    preload_files()

    return app


def preload_files():
    filenames = [
        '2004_v6.xml',
        'EA_AIP_DS_FULL_20170701.xml'
    ]

    for filename in filenames:
        filepath = resource_filename(__name__, f'../samples/{filename}')
        # filepath = os.path.join('../samples', filename)

        dataset = cache.create_dataset(filepath)

        dataset.process()


if __name__ == '__main__':
    app = create_app(config_file=resource_filename(__name__, 'config.yml'))
    app.run(host="0.0.0.0", port=5000)
