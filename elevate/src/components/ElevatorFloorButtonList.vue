<template>
  <h1> ______ </h1>
  <ElevatorFloorButton :floor="1"></ElevatorFloorButton>
  <ElevatorFloorButton :floor="2"></ElevatorFloorButton>
  <ElevatorFloorButton :floor="3"></ElevatorFloorButton>
  <ElevatorFloorButton :floor="4"></ElevatorFloorButton>
  <ElevatorFloorButton :floor="5"></ElevatorFloorButton>
  <h1> ______ </h1>
</template>

<script>
import ElevatorFloorButton from "@/components/ElevatorFloorButton";

export default {
  name: "ElevatorFloorButtonList",
  components: {
    ElevatorFloorButton
  }
}
</script>

<style scoped>

</style>