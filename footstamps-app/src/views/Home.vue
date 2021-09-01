<template>
  <div>
    <b-container fluid>
      <b-row>
        <b-col><SearchPane v-on:model-results="updateMap" v-on:show-more="showMore"/></b-col>
        <b-col cols="8"><MapPane v-bind:modelResults="modelResults" v-bind:coordinates="coordinates" :key="componentKey"/></b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
// @ is an alias to /src
// import HelloWorld from '@/components/HelloWorld.vue'
import SearchPane from '@/components/SearchPane.vue'
import MapPane from '@/components/MapPane.vue'

export default {
  name: 'home',
  components: {
    SearchPane, MapPane
  },
  data () {
    return {
      coordinates: [-84.4, 33.7],
      allResults: {
        results: []
      },
      modelResults: [],
      display: 0,
      componentKey: 0
    }
  },
  methods: {
    updateMap (results) {
      this.coordinates = results['coordinates']
      this.allResults = results
      this.display = results['display']
      this.modelResults = results['results'].slice(0, this.display)
      this.componentKey += 1
      const numDisplay = {
        display: this.display,
        totalResults: this.allResults['results'].length
      }
      this.$emit('update-display', numDisplay)
    },
    showMore () {
      if ((this.display + 25) >= this.allResults['results'].length) {
        this.display = this.allResults['results'].length
      } else {
        this.display += 25
      }
      this.modelResults = this.allResults['results'].slice(0, this.display)
      this.componentKey += 1
      const numDisplay = {
        display: this.display,
        totalResults: this.allResults['results'].length
      }
      this.$emit('update-display', numDisplay)
    }
  }
}
</script>

<style lang="scss">
</style>
