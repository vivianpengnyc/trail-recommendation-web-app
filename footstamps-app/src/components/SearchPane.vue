<template>
    <div id="search-pane">
        <b-container fluid>
            <b-row>
                <b-col>
                    <label for="search-box">Search for:</label>
                    <b-form-textarea id="search-box" size="lg" rows="3" v-model="text" placeholder='Enter trail characteristics'>{{ text }}</b-form-textarea>
                </b-col>
            </b-row>
            <b-row>
                <b-col>
                    <label for="within">Within</label>
                    <b-form id="within" class="mt-1" inline>
                        <b-form-input id="miles" class="w-25" size="sm" v-model="miles" placeholder="20">{{ miles }}</b-form-input>
                        <span id="label_span"> miles</span>
                    </b-form>
                </b-col>
            </b-row>
            <b-row>
                <b-col>
                    <label for="park-form">of</label>
                        <b-form id="park-form" class="mt-1">
                        <b-form-input id="park" class="w-100" size="sm" v-model="park" placeholder="Atlanta, GA">{{ park }}</b-form-input>
                </b-form>
                </b-col>
            </b-row>
            <b-row>
                <b-col>
                    <label for="distance">Preferred trail length</label>
                <b-form id="distance" inline>
                    <b-form-input id="length" class="w-25" size="sm" v-model="length" placeholder="4">{{ length }}</b-form-input>
                    <span id="label_span"> miles</span>
                </b-form>
                </b-col>
            </b-row>
            <b-row>
                <b-col><label for="profile">Hike profile</label></b-col></b-row>
            <b-row>
                <b-col cols="1" class="mr-0 pr-0">
                    <span style="color: #005c2c"><font-awesome-icon class="fa-lg" icon="hiking"/></span>
                </b-col>
                <b-col>
                    <b-form-select v-model="selected" :options="options" size="sm"></b-form-select>
                </b-col>
            </b-row>
            <b-row class="mt-4">
                <b-col class="col-3">
                        <input class="btn btn-primary" type="submit" value="Search" v-on:click="runModel"/>
                </b-col>
                <b-col class="col-5">
                        <input class="btn btn-primary" type="submit" value="Show More Results" v-on:click="showMore"/>
                </b-col>
                <b-col class="col-3">
                        <input class="btn btn-primary" type="submit" value="Clear All" v-on:click="clearAll"/>
                </b-col>
            </b-row>
            <b-row class="mt-2">
            <label>Trail Marker Legend</label>
            </b-row>
            <b-row class="mt-1">
            <svg height="25">
                <circle r="5" cx="10" cy="10" width="15" height="15" stroke="gray" :fill=color(20)></circle>
                <circle r="5" cx="30" cy="10" width="15" height="15" stroke="gray" :fill=color(40)></circle>
                <circle r="5" cx="50" cy="10" width="15" height="15" stroke="gray" :fill=color(60)></circle>
                <circle r="5" cx="70" cy="10" width="15" height="15" stroke="gray" :fill=color(80)></circle>
                <circle r="5" cx="90" cy="10" width="15" height="15" stroke="gray" :fill=color(100)></circle>
            </svg>
            </b-row>
            <b-row>
                <small>Darker trail markers indicate a better match.</small><br/>
                <small>App is optimized for full-screen or higher resolutions. Mobile not supported.</small><br/>
                <small>Results may take some time to populate. Search radius less than 50 miles for best performance.</small>
            </b-row>
            <b-row class="author mt-5">
                Created by Allison Feldman, Beth Parrott<br/>
                Vivian Peng, Yenny Su, Lu Zhang
            </b-row>
        </b-container>
    </div>
</template>
<script>
import $backend from '../backend'
import * as d3 from 'd3'

let colorScale = d3.scaleSequential(d3.interpolateYlGn).domain([0, 100])
export default {
  name: 'SearchPane',
  data () {
    return {
      text: '',
      miles: '20',
      park: 'Atlanta, GA',
      length: '4',
      selected: 'Intermediate',
      display: 25,
      options: [
        { value: 'Intermediate', text: 'Select Level' },
        { value: 'Easy', text: 'Easy' },
        { value: 'Intermediate', text: 'Intermediate' },
        { value: 'Difficult', text: 'Difficult' }
      ]
    }
  },
  props: {},
  methods: {
    runModel () {
      this.display = 25
      $backend.runModel(this.text, this.miles, this.park, this.length, this.selected)
        .then(responseData => {
          responseData.display = 25
          this.$emit('model-results', responseData)
        }).catch(error => {
          this.error = error.message
        })
    },
    showMore () {
      this.display += 25
      this.$emit('show-more', this.display)
    },
    clearAll () {
      location.reload()
    },
    color (score) { return colorScale(score) }
  }
}
</script>
<style lang="scss" scoped>

    .author {
        font-size: x-small
    }

    #search-box {
        font-size: small;
    }

    #miles {
        background: transparent;
        border: none;
        border-bottom: 1px solid #000000;
        outline:none;
        box-shadow:none;
    }
    #park  {
        background: transparent;
        border: none;
        border-bottom: 1px solid #000000;
        outline:none;
        box-shadow:none;
    }
    #length  {
        background: transparent;
        border: none;
        border-bottom: 1px solid #000000;
        outline:none;
        box-shadow:none;
    }
    label {
        font-size: smaller;
        font-weight: bold;
        margin-top: 15px;
    }
    #label_span {
        font-size: smaller;
    }
    textarea.form-control {
        font-size: x-small;
    }
    .btn-primary {
     background-color: #005c2c;
     border-color: #005c2c;
     width: 100%;
     font-size: smaller;
     padding-left: 0%;
     padding-right: 0%;
    }
</style>
