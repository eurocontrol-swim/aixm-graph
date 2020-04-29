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
  <div id=main>
    <navbar></navbar>
    <dataset></dataset>
    <graph></graph>
    <alert></alert>
  </div>

</template>

<script>
import M from 'materialize-css';
import Navbar from './navbar/Navbar.vue';
import Dataset from './sidebar/Dataset.vue';
import Graph from './graph/Graph.vue';
import Alert from './Alert.vue';


export default {
  name: 'Main',
  components: {
    Navbar,
    Dataset,
    Graph,
    Alert,
  },
  methods: {
    initMateriazeComponents() {
      document.addEventListener('DOMContentLoaded', () => {
        M.Dropdown.init(document.querySelectorAll('.dropdown-trigger'), {});
        M.Modal.init(document.querySelectorAll('.modal'), {});
        M.Sidenav.init(document.querySelectorAll('.sidenav'), {});
        M.Collapsible.init(document.querySelectorAll('.collapsible'), {});
        M.Tooltip.init(document.querySelectorAll('.tooltipped'), {});
        M.FormSelect.init(document.querySelectorAll('select'), {});
      });
    },
  },
  created() {
    this.initMateriazeComponents();
  },
};
</script>

<style>

#main {
  height: 100%;
}

</style>
