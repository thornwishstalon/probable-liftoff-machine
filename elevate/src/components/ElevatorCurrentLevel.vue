<template>
  <h2>[ {{currentLevel}} ]</h2>
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
h2{
  color: #2c3e50;
}

</style>