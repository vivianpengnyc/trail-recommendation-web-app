# Data Scraping, Processing, and Model Training Code 
This collection of scripts and files were used to collect the data, clean/process it, and then train the TF-IDF vectorizer.
Data was collected by scraping two websites: AllTrails, and HikingProject.

## Setup
To run these scripts, it is best to create an environment that is identical to the one used during development. 
Setup files have been extracted for this purpose.

1) Install conda. You can do this by installing [Anaconda](https://www.anaconda.com/products/individual) 
or [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
2) Add conda-forge as a channel, and then create an environment using the provided requirements.txt.
```
conda config --append channels conda-forge
conda create --name ENV_NAME --file requirements.txt
```

3) Alternatively directly create an environment with the provided .yml file
```
conda env create -f dva.yml
```
4) Activate environment. **Always** make sure you are on this environment before running scripts.
```
conda activate ENV_NAME
```
5) Sign up for an [API Key from HikingProject](https://www.hikingproject.com/data).

6) Run scripts as noted below.

## Running Scripts
There are 3 steps: Scraping, ETL, and Training. Simply run each executable file in the order
that they are presented below (e.g all files under 'scraping' then all files under
'etl', file 'TrailsList.ipynb' then 'hike_scraper.py', etc). The files under Scraping may take 
a long time and you may be denied service a few times.
If looking for a subset of files to run, recommend those under \etl.

Note that 4 files are denoted by *, as 1 requires an API key to be inserted 
and all 4 modify the MongoDB in real time. The sections of code that permanently modify our MongoDB 
collections are commented out, you must uncomment them if you want to modify our database (which is not recommended).
You can run the files leaving those sections commented and explore the variables and methods. 

If electing to modify our MongoDB collections (not recommended): Do not run these files out of order, or 
without running all of them before moving on to the app code.

```
project
│   README.txt
│   FileFlow.png
│   requirements.txt
│   dva.yml  
│
└─── scraping
│   │
│   └─── alltrails
│       │   TrailsList.ipynb 
│       │   trails_20201003.csv
│       │   hike_scraper.py* CAUTION: OVERWRITES MongoDB DATA
│   │
│   └─── hikingproject
│       │   hikingproject_crawl.py
│       │   HPtrail_ids.csv
│       │   hikingproject_apicalls.py* API KEY NEEDED, CAUTION: OVERWRITES MongoDB DATA
│       │   hikingproject_comments.py
│   
└─── etl
│    │   find_matching_trails.py
│    │   HP_AT_matching_trails.json
│    │   combine_hp_at.py* CAUTION: OVERWRITES MongoDB DATA
│    │   comments.json
│   
└─── data_processing_training
    │   text_prep.py* CAUTION: OVERWRITES MongoDB DATA
```
