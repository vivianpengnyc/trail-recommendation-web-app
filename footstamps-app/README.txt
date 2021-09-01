########################
###    Footstamps    ###
########################

Created by Allison Feldman, Beth Parrott, Vivian Peng, Yenny Su, and Lu Zhang

##  Description
The Footstamps application is currently deployed on Heroku. Please visit https://footstamps.herokuapp.com/. The app is best viewed at higher resolution.

Footstamps is an interactive hiking trail recommendation app. Users provide parameters such as trail characteristics, distance, location, and length into the application. The application passes these inputs into a machine learning recommendation model to provide trail recommendations and displays recommendations on an interactive map visualization with 3D rendering capabilities.

##  User Inputs
- Trail characteristics: Enter descriptive or identifying keywords for desired trail characteristics, e.g., "lake, solitude, flat, remote, forested, quiet".
- Radius: Enter search radius, e.g., "50 miles"
- Location: Enter location for center of search radius, e.g., "Mt. Rainier National Park"
- Preferred Trail Length: Enter desire trail length in miles, e.g., "10 miles"
- Hike Profile: Select desired trail difficulty, e.g., "Intermediate"

Click "Search" to populate results on map. The color of the trail marker indicate the degree of match for the trail. The darker the color, the higher the match score. Trail markers can be interacted with via clicking to initiate pop-up with trail information. Map can also be panned, zoomed, and tilted horizonally to see 3D topographical rendering.

##  How It Works
This application uses Flask & Flask-RestPlus to create a minimal REST style API, and let's VueJs + vue-cli handle the front end and asset pipline.
Data from the Python server to the Vue application is passed by making Ajax requests using Axios. The frontend visualization is created using the ArcGIS Map API.

After the user inputs data and clicks "Search", model parameters are passed to the Flask Python server. The Python server makes a call to the ArcGIS Geoencoding API to return GPS coordinates for the location input. The Python server uses the returned GPS coordinates in a spatial MongoDB query and returns trails within the user-specified radius of the GPS coordinates. Filtered trails are fed through the TrailScoring recommendation model. Recommended trail information and score is passed to the frontend Vue application. The ArcGIS Javascript is called and renders user inputs and model trail outputs on the interactive geospatial map visualization.

##  Features
- Minimal Flask 1.0 App
- Flask-RestPlus http://flask-restplus.readthedocs.io
- vue-cli 3 + yarn https://github.com/vuejs/vue-cli/blob/dev/docs/README.md
- Vue Router https://router.vuejs.org/
- Axios https://github.com/axios/axios/
- ArcGIS https://developers.arcgis.com/javascript/
- MongoDB https://docs.mongodb.com/

##  Pre-Installation Setup
Before getting started, you should have the following installed and running
- Yarn https://yarnpkg.com/en/docs/install#mac-stable
- Vue CLI 3 https://cli.vuejs.org/guide/installation.html
- Python 3.6
- Pipenv
- Heroku Cli (if deploying to Heroku)

Installation has not been tested on Mac OS.

##  Installation Running Local Server
- Start in /footstamps-app directory
- Set up virtual environment with Python 3.6
- Install dependencies using pipenv and activate it:
	pipenv install --dev
	pipenv shell
- Install JS dependencies
	yarn install

##  Important Files
 -------------------------------------------------------------------------
| Location                   |  Content                                   |
|----------------------------|--------------------------------------------|
| `/app`                     | Flask Application                          |
| `/app/api`                 | Flask Rest Api (`/api`)                    |
| `/app/api/Trailscoring.py` | Model Script                    		      |
| `/app/api/geocode.py`      | Location Geocoding Script                  |
| `/app/api/resources.py`    | Flask Rest API Definitions                 |
| `/app/api/pickle/`         | Model Pickle Files                    	  |
| `/app/client.py`           | Flask Client (`/`)                         |
| `/src`                     | Vue App                                    |
| `/src/main.js`             | JS Application Entry Point                 |
| `/src/App.vue`             | Vue App Entry Point                        |
| `/src/views/`              | Vue Home component           	          |
| `/src/components/`         | Vue SearchPane and MapPane components      |
| `/public/index.html`       | Html Application Entry Point (`/`)         |
| `/public/static`           | Static Assets                              |
| `/dist/`                   | Bundled Assets Output 			          |
 -------------------------------------------------------------------------

##   Running Development Server
- Run Flask API development Server:
	python run.py
- From another tab or terminal in the same /footstamps-app directory, start the webpack dev server:
	yarn serve

The Vuejs application will be served from `localhost:8080` and the Flask Api and static files will be served from `localhost:5000`.

##   Footstamps MongoDB Database
The Footstamps MongoDB Database contains 79,127 trails, 2,839,366 user reviews, and 738,868 comments and is hosted on Google Cloud Platform. The Footstamps queries this database to fetch trail information.
The MongoDB database is publicly accessible. We recommend using the PyMongo API.

Host: 35.227.61.30
User: user1
Database: outdoor
Collection: trails

##   Heroku Deployment
Heroku's nodejs buidlpack will handle install for all the dependencies from the `packages.json` file. It will then trigger the `postinstall` command which calls `yarn build`. This will create the bundled `dist` folder which will be served by whitenoise.

The Python buildpack will detect the `Pipfile` and install all the python dependencies.

##   Acknowledgements

The application is built on top of a Flask-Vuejs template provided here:
https://github.com/gtalarico/flask-vuejs-template