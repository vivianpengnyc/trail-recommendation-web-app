<template>
  <div id="app">
    <div :key="componentKey">
      <b-navbar>
        <b-navbar-brand href="#">
          <img src="@/assets/footstamps-logo.png" class="d-inline-block align-top">
        </b-navbar-brand>
        <b-collapse is-nav id="nav_collapse">
          <b-navbar-nav class="ml-auto" id="results">
            <b-nav-text>Showing {{this.display}} of {{this.totalResults}} results</b-nav-text>
          </b-navbar-nav>
          <b-navbar-nav class="ml-auto">
            <b-nav-text class="d-inline-flex flex-column">
              <span>Final Project</span>
              <span>CSE 6242</span>
              <span>Fall 2020</span>
            </b-nav-text>
          </b-navbar-nav>
        </b-collapse>
      </b-navbar>
      </div>

    <router-view v-on:update-display="updateDisplay"/>

  </div>
</template>

<script>
export default {
  name: 'App',
  data () {
    return {
      display: 0,
      totalResults: 0,
      componentKey: 0
    }
  },
  methods: {
    updateDisplay (numDisplay) {
      this.display = numDisplay['display']
      this.totalResults = numDisplay['totalResults']
      this.componentKey += 1
    }
  }
}
</script>

<style lang="scss">
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  //text-align: center;
  color: #2c3e50;
}
#nav {
  padding: 30px;
  a {
    font-weight: bold;
    color: #2c3e50;
    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
#plus {
  padding: 0 20px 0 20px;
  display: inline-block;
  font-size: 50px;
  vertical-align: top;
  line-height: 100px;
}

.navbar-light {
   background-color: #faf6ee;
   height: 75px;
}

.navbar .navbar-brand {
  position: absolute;
  left: 0;
  padding-top: 0px;
  height: 50px;
}
.navbar .navbar-brand img {
  height: 50px;
}

.navbar .navbar-nav {
  fill: true;
}

.navbar-text {
  font-size: smaller;
}

#results {
  font-size: larger;
  font-weight: bold;
}
.nav-link {
  font-size: smaller;
}

</style>
