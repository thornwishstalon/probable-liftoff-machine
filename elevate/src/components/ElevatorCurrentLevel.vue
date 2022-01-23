<template>
  <h2>Current Level : {{currentLevel}} </h2>
</template>

<script>
export default {
  name: "ElevatorCurrentLevel",
  computed:{
    currentLevel (){
      return this.$store.getters.currentLevel
    }
  }
}
</script>

<style scoped>

</style>