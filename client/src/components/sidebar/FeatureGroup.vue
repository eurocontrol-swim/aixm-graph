// Copyright 2020 EUROCONTROL
// ==========================================

// Redistribution and use in source and binary forms, with or without modification, are permitted
// provided that the following conditions are met:

// 1. Redistributions of source code must retain the above copyright notice, this list of conditions
//    and the following disclaimer.
// 2. Redistributions in binary form must reproduce the above copyright notice, this list of
//    conditions and the following disclaimer in the documentation and/or other materials provided
//    with the distribution.
// 3. Neither the name of the copyright holder nor the names of its contributors may be used to
//    endorse or promote products derived from this software without specific prior written
//    permission.

// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
// IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
// FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
// CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
// WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
// ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

// ==========================================

// Editorial note: this license is an instance of the BSD license template as provided by the Open
// Source Initiative: http://opensource.org/licenses/BSD-3-Clause

// Details on EUROCONTROL: http://www.eurocontrol.int

<template>
  <div>
     <li @click="featureGroupSelected" class="feature-item">
        <a class="waves-effect collection-item active" href="#!" >
             {{ featureGroup.name}} ({{ featureGroup.totalCount }})
          <i class="material-icons"
             :style="[featureGroup.hasBrokenXlinks ? {color: '#ee6e73'} : {color: '#26a69a'}]">
             {{ icon }}
          </i>
        </a>
     </li>
  </div>
</template>

<script>
import EventBus from '../event-bus';

export default {
  name: 'FeatureGroup',
  props: ['featureGroup', 'datasetId'],
  methods: {
    featureGroupSelected() {
      EventBus.$emit('feature-group-selected', this.datasetId, this.featureGroup.name);
    },
  },
  computed: {
    icon() {
      return this.featureGroup.hasBrokenXlinks ? 'report' : 'done';
    },
  },
};
</script>

<style scoped>

.feature-item > a {
    height: 35px;
    line-height: 35px;
}

.feature-item > a > i.material-icons{
    height: 35px;
    line-height: 35px;
}
</style>
