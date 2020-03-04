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

import sys

from flask import Flask

from aixm.web_app.views import aixm_blueprint

sys.path.insert(0, '/media/alex/Data/dev/work/eurocontrol/aixm/')

from pkg_resources import resource_filename

from aixm.parser import process_aixm
from aixm.utils import load_config, get_samples_filepath

# TODO: display broken links
# TODO: filter features pon their keys
# TODO: upload AIXM file view
# TODO: download skeleton file view
# TODO: apply pagination in case of big graph

app = Flask(__name__)
app.register_blueprint(aixm_blueprint)

app_config = load_config(filename=resource_filename(__name__, 'config.yml'))
app.config.update(app_config)


if __name__ == '__main__':
    # filepath, ns_message = get_samples_filepath('BD_2019-01-03_26fe8f56-0c48-4047-ada0-4e1bd91ed4cf.xml'), \
    #                        "http://www.aixm.aero/schema/5.1/message"
    filepath, ns_message = get_samples_filepath('EA_AIP_DS_FULL_20170701.xml'), \
                           "http://www.aixm.aero/schema/5.1.1/message"

    # feature_elements = process_aixm(filepath=filepath, element_tag=f'{{{ns_message}}}hasMember', config=app.config)

    app.run(host="0.0.0.0", port=3000)
