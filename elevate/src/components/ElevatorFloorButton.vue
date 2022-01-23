<template>
  <button-spinner
      @click="onClick"
      v-bind="isLoading"
      :disabled="isLoading"
      :class="{ active: isActive(floor) }"
  >
    {{ floor }}
  </button-spinner>
</template>

<script>

import ButtonSpinner from 'vue-button-spinner'
import axios from "axios";

export default {
  name: "ElevatorFloorButton",
  components: {
    ButtonSpinner
  },
  props: {
    floor: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      statusMessage: this.floor,
      isLoading: false,
    }
  },
  methods: {
    async pushTrip() {
      try {
        this.isLoading = true
        const tripParams = new URLSearchParams();
        tripParams.append('next', this.floor.toString());
        const response = axios.put("http://192.168.4.1/floor", {params: tripParams})
        console.log(response)
        this.isLoading = false
      } catch (err) {
        if (err.response) {
          // client received an error response (5xx, 4xx)
          console.log("Server Error:", err)
        } else if (err.request) {
          // client never received a response, or request never left
          console.log("Network Error:", err)
        } else {
          console.log("Client Error:", err)
        }
      }
    },
    isActive(floor) {
      return this.$store.getters.isActive(floor)
    },
    onClick() {
      this.pushTrip()
    },
  }
}
</script>

<style scoped>

button {
  background-color: #007faf;
}

button.active {
  background-color: #eec754;
}

</style>