<template>
  <div id="modal1" class="modal bottom-sheet red " ref="alertModal">
    <div class="modal-content red alert-modal-content center-align">
      <span class="valign-wrapper">
        <i class="material-icons left">error</i> {{ message }}
      </span>
    </div>
  </div>
</template>

<script>
import M from 'materialize-css';
import EventBus from './event-bus';

export default {
  name: 'Alert',
  data() {
    return {
      message: '',
    };
  },
  created() {
    EventBus.$on('alert', (alertMessage) => {
      this.message = alertMessage;
      M.Modal.getInstance(this.$refs.alertModal).open();
    });
  },
};
</script>

<style >

.alert-modal-content {
  padding: 0;
  color: white;
}

</style>
