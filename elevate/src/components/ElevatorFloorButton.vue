<template>
  <button @click="pushTrip()" :class="{ active: isActive() }">
    {{ floor }}
  </button>

</template>

<script>

import axios from "axios";
import image from "@/assets/spinner.gif"

export default {
  name: "ElevatorFloorButton",
  props: {
    floor: {
      type: Number,
      required: true,
    }
  },
  data: () => {
    return {
      image: image,
      isLoading: false
    }
  },
  methods: {
    async pushTrip() {
      try {
        const tripParams = new URLSearchParams();
        tripParams.append('next', this.floor.toString());
        const response = axios.put("http://192.168.4.1/floor", {params: tripParams})
        console.log(response)
        this.isLoading = false
        this.status = true
      } catch (err) {
        this.status = false
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
    isActive() {
      return this.$store.getters.isActive(this.floor)
    }
  }
}
</script>

<style scoped>

button {
  background-color: #007faf;
  margin: 5px;
  font-size: 30px;
  color: white;
}

button.active {
  background-color: #eec754;
}

</style>