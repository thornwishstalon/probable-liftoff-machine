<template>
  <img alt="Vue logo" src="./assets/logo.png">
  <ElevatorCurrentLevel/>
  <ElevatorFloorButtonList/>
</template>

<script>
import ElevatorCurrentLevel from '@/components/ElevatorCurrentLevel.vue'
import ElevatorFloorButtonList from "@/components/ElevatorFloorButtonList";
import axios from "axios";
import {connect} from "mqtt";


export default {
  name: 'App',
  components: {
    ElevatorFloorButtonList,
    ElevatorCurrentLevel
  },
  data: () => {
    return {
      connection: {
        host: 'localhost',
        port: 9001, // websockets use port 9001 instead of 1883
        connectTimeout: 4000, // Time out
        reconnectPeriod: 4000, // Reconnection interval
        // Certification Information
        clientId: 'vue-7CD7',

      },
      client: {
        connected: false
      },
      subscription: [
        {
        topic: 'liftoff/move/to', //#
        qos: 0,
        },
        {
          topic: 'liftoff/update/next', //#
          qos: 0,
        },
      ],

    }
  },
  methods: {
    async updateState() {
      try {
        const url = 'http://192.168.4.1/state'
        const response = await axios.get(url)
        this.$store.commit('updateState', response.data)

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
    createConnection() {
      const {host, port, ...options} = this.connection
      const connectUrl = `ws://${host}:${port}`
      try {
        this.client = connect(connectUrl, options)
        this.doSubscribe()
      } catch (error) {
        console.log('mqtt.connect error', error)
      }
      this.client.on('connect', () => {
        console.log('Connection succeeded!')
      })
      this.client.on('error', error => {
        console.log('Connection failed', error)
      })
      // handle incoming messages!
      this.client.on('message', (topic, message) => {
        var uint8array = new TextEncoder().encode(message);
        var message_object = JSON.parse(new TextDecoder().decode(uint8array));
        // distribute message accordingly
        if (topic === "liftoff/move/to") {
          this.$store.commit('updateLevel', message_object)
        }
        if (topic === "liftoff/update/next") {
          this.$store.commit('updateNextQueue', message_object)
        }
      })
    },
    destroyConnection() {
      if (this.client.connected) {
        try {
          this.client.end()
          this.client = {
            connected: false,
          }
          console.log('Successfully disconnected!')
        } catch (error) {
          console.log('Disconnect failed', error.toString())
        }
      }
    },
    doSubscribe() {
      for (const {topic, qos} of this.subscription){
        console.log(topic)
        this.client.subscribe(topic, {qos}, (error, res) => {
          if (error) {
            console.log('Subscribe to topics error', error)
            return
          }
          this.subscribeSuccess = true
          console.log('Subscribe to topics res', res)
        })
      }
    },
  },
  doUnSubscribe() {
    for (const {topic} of this.subscription){
      this.client.unsubscribe(topic, error => {
        if (error) {
          console.log('Unsubscribe error', error)
        }
      })
    }
  },
  mounted() {
    console.log('get server state')
    this.updateState()
    console.log('init mqtt')
    this.createConnection()

  },
  unmounted() {
    this.doUnSubscribe()
    this.destroyConnection()
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
