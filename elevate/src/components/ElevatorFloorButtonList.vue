<template>
  <h1>Floors</h1>
  <ElevatorFloorButton :floor="1"></ElevatorFloorButton>
</template>

<script>
import ElevatorFloorButton from "@/components/ElevatorFloorButton";

export default {
  name: "ElevatorFloorButtonList",
  components:{
    ElevatorFloorButton
  }
}
</script>

<style scoped>

</style>