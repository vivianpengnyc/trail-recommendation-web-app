<template>
  <div class="mt-2"></div>
</template>

<script>
import { loadModules } from 'esri-loader'
import * as d3 from 'd3'

export default {
  name: 'MapPane',
  props: ['modelResults', 'coordinates'],
  mounted () {
    // lazy load the required ArcGIS API for JavaScript modules and CSS
    loadModules(['esri/Map', 'esri/views/SceneView', 'esri/Graphic', 'esri/layers/GraphicsLayer', 'esri/symbols/SimpleMarkerSymbol', 'esri/PopupTemplate', 'esri/widgets/DirectLineMeasurement3D', 'esri/widgets/Expand', 'esri/widgets/BasemapGallery', 'esri/Basemap', 'esri/widgets/BasemapGallery/support/PortalBasemapsSource'], { css: true })
      .then(([ArcGISMap, SceneView, Graphic, GraphicsLayer, SimpleMarkerSymbol, PopupTemplate, DirectLineMeasurement3D, Expand, BasemapGallery, Basemap, PortalSource]) => {
        const map = new ArcGISMap({
          basemap: 'topo-vector',
          ground: 'world-elevation'
        })

        this.view = new SceneView({
          container: this.$el,
          map: map,
          center: this.coordinates,
          zoom: 8,
          environment: {
            lighting: {
              date: new Date('October 27, 2020 18:00:00 UTC'),
              directShadowsEnabled: true,
              ambientOcclusionabled: true
            },
            atmosphereEnabled: true,
            atmosphere: {
              quality: 'high'
            },
            starsEnabled: true
          }
        })

        // add a measure widget
        var measurement = new DirectLineMeasurement3D({
          view: this.view,
          unit: 'kilometers',
          label: 'Distance Measurement Widget'
        })

        var measureExpand = new Expand({
          view: this.view,
          content: measurement
        })

        // close the expand whenever a basemap is selected
        measurement.watch('measurement', function () {
          var mobileSize =
            this.view.heightBreakpoint === 'xsmall' ||
            this.view.widthBreakpoint === 'xsmall'

          if (mobileSize) {
            measureExpand.collapse()
          }
        })
        this.view.ui.add(measureExpand, 'top-right')

        // filter availiable basemap options
        var allowedBasemapTitles = ['Topographic', 'Imagery Hybrid', 'Terrain with Labels']
        var source = new PortalSource({
          // filtering portal basemaps
          filterFunction: (basemap) => allowedBasemapTitles.indexOf(basemap.portalItem.title) > -1
        })

        // Create a BasemapGallery widget instance and set
        // its container to a div element
        var basemapGallery = new BasemapGallery({
          view: this.view,
          container: document.createElement('div'),
          source: source
        })

        var bgExpand = new Expand({
          view: this.view,
          content: basemapGallery
        })

        // close the expand whenever a basemap is selected
        basemapGallery.watch('activeBasemap', function () {
          var mobileSize =
            this.view.heightBreakpoint === 'xsmall' ||
            this.view.widthBreakpoint === 'xsmall'

          if (mobileSize) {
            bgExpand.collapse()
          }
        })

        this.view.ui.add(bgExpand, 'top-right')

        // check if results exist
        if (this.modelResults.length > 0) {
          const graphicsArr = []

          // get min and max score, scale for score and color
          const minScore = d3.min(this.modelResults, function (d) { return d['score'] })
          const maxScore = d3.max(this.modelResults, function (d) { return d['score'] })
          const colorScale = d3.scaleSequential(d3.interpolateYlGn).domain([minScore, maxScore])

          // loop through results and create Esri graphic
          for (var i = 0; i < this.modelResults.length; i++) {
            const trail = this.modelResults[i]

            const symbolDef = {
              style: 'circle',
              color: colorScale(trail['score']),
              size: '15px',
              opacity: '100%'
            }

            // Define popup with html
            const popUp = {
              title: `<b><p style="font-size: 20px">${trail['name']}</p></b>`
            }
            // Check to see if hiking project or alltrails source
            const trailSource = trail['url'].includes('alltrails') ? 'AllTrails' : 'HikingProject'
            popUp.content = `
              <table>
                <tr>
                  <td style="padding-right: 10px"><b>Score:</b></td>
                  <td>${trail['score']}</td>
                </tr>
                <tr>
                  <td style="padding-right: 10px"><b>Difficulty:</b></td>
                  <td>${trail['difficulty']}</td>
                </tr>
                <tr>
                  <td style="padding-right: 10px"><b>Distance:</b></td>
                  <td>${trail['length']} miles</td>
                </tr>
                <tr>
                  <td style="padding-right: 10px"><b>Elevation:</b></td>
                  <td>${trail['elevation']} ft</td>
                </tr>
                <tr>
                  <td style="padding-right: 10px"><b>Description:</b></td>
                  <td>${trail['description']}</td>
                </tr>
                <tr>
                  <td style="padding-right: 10px"><b>Source:</b></td>
                  <td><a href=${trail['url']}>${trailSource}</a></td>
                </tr>
                <tr>
                  <td style="padding-right: 10px"><b>Directions:</b></td>
                  <td><a href=${trail['map']}>Click Here</a></td>
                </tr>
              </table>`

            const graphic = new Graphic({
              geometry: {
                type: 'point',
                latitude: trail['loc']['coordinates'][1],
                longitude: trail['loc']['coordinates'][0]
              },
              symbol: new SimpleMarkerSymbol(symbolDef),
              popupTemplate: popUp
            })
            graphicsArr.push(graphic)
          };

          // create new layer
          var trailLayer = new GraphicsLayer({
            graphics: graphicsArr
          })

          map.add(trailLayer)
        }
      })
  },
  beforeDestroy () {
    if (this.view) {
      // destroy the map view
      this.view.destroy()
    }
  }
}

</script>

<style scoped>
  div {
    padding: 0;
    margin: 0;
    width: 100%;
    height: 100%;
  }
</style>
