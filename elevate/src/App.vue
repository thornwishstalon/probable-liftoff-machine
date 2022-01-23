<template>
  <img alt="Vue logo" src="./assets/logo.png">
  <ElevatorCurrentLevel/>
  <ElevatorFloorButtonList/>
</template>

<script>
//import HelloWorld from './components/HelloWorld.vue'
import ElevatorCurrentLevel from '@/components/ElevatorCurrentLevel.vue'
import ElevatorFloorButtonList from "@/components/ElevatorFloorButtonList";
import axios from "axios";

export default {
  name: 'App',
  components: {
    ElevatorFloorButtonList,
    ElevatorCurrentLevel
  },
  methods:{
    async updateState ()  {
      try {
        const url = 'http://191.168.4.1/state'
        const response = await axios.get(url)
        this.$store.commit('updateState', response)

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
    }
  },
  mounted() {
    console.log('mounted')
    this.updateState()
    console.log('init fetch')
    setInterval(() => {
      this.updateState()
    }, 1000)

  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
