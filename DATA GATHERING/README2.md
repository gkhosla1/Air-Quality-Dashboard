# Data Gathering Flow

Files for every step of the data manipulation process are in this folder. The process is outlined below for those curious:

 1. IQ Air Data Scrape (iqair_scrape.ipynb): scrapes data from IQ Air's website
    - input file(s): iso3.csv
    - output file: iq_air.csv
    - required packages: requests, beautifulsoup4, pandas, numpy
 2. Population Data Cleaning (pop_data_clean.ipynb): cleans data downloaded from UN
    - input file(s): pop_data.csv, iso3.csv
    - output file: pop_clean.csv
    - required packages: pandas, numpy
 3. Joining Air Quality and Population Datasets (final_join.ipynb): joins datasets for use in dashboard
    - input file(s): iq_air.csv, pop_clean.csv
    - output file: final_data.csv
    - required packages: pandas, tqdm.notebook (tqdm), difflib (get_close_matches)
