# TCGA Gene Expression Data Downloader

## Overview
The aim of this project is to scrape (download) all gene expression datafiles for each TCGA cancer cohort from the Xena Browser (TCGA hub) website. The target files are named "IlluminaHiSeq pancan normalized" for each cancer cohort in the TCGA project. 

## Key Features
- Downloads all target files in gzip format
- Decompresses the downloaded files to TSV (tab-separated value) format
- Supports both web scraping and public API access (if available)
- Implemented using Selenium Python

## Usage
1. Ensure you have Python and the required dependencies installed (Selenium, requests, gzip, etc.).
2. Run the script to initiate the data download process.
3. The downloaded TSV files will be saved in the local directory.

## Dependencies
- Python 3.x
- Selenium Python
- Requests library
- gzip library

