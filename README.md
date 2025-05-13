# Question 3 - Group 3

## Overview
This code will scrapes athlete height data for NCAA men's and women's swimming and volleyball teams, performs  analysis, and identifies the tallest and shortest athletes in each category.

## Requirements
- Python 3.x
- BeautifulSoup4
- requests
- pandas
- numpy

## Installation
`install beautifulsoup4 requests pandas numpy`


## Data Collection
The program scrapes athlete height data from NCAA team rosters for:
1. Men's Swimming
2. Women's Swimming
3. Men's Volleyball
4. Women's Volleyball

## Output Files
The program generates four CSV files:
- `mens_swimming_heights.csv`
- `womens_swimming_heights.csv`
- `mens_volleyball_heights.csv`
- `womens_volleyball_heights.csv`

## Analysis Performed
1. Calculates average height for each of the four categories
2. Identifies the 5 tallest and 5 shortest athletes in each category (with ties included)
3. Compares average heights between swimmers and volleyball players

## How to Run

`python athlete_height_analysis.py`

## Expected Output
1. CSV files with all athlete names and heights for each category
2. Printed average heights for each category
3. Printed lists of tallest and shortest athletes for each category
4. Comparative analysis of swimmer vs volleyball player heights

## Notes
- The script handles ties when identifying tallest/shortest athletes
- Height data is standardized to inches for comparison
- Results include both printed output and saved CSV files
