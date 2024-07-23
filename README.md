<<<<<<< HEAD
# GoogleTakeout
Python scripts to analyze YouTube watch history data, utilizing NLP, LDA, and data visualization tools for insights.

1. Instructions
Do not change directories: Keep the directory structure as is.

2. Place your watch history file: Drop your watch-history.html file into the history folder directory.

3. Run the scripts in order: Execute each Python file in the following order to process your data:
  "01_data_collection.py"
  "02_data_preprocessing.py"
  "03_nlp_analysis.py"
  "04_lda_analysis.py"
  "05_active_periods_analysis.py"
   
4. Bonus file (Optional): 
   city names converter.py is not necessary for the main analysis as its output is already included. This script requires an internet connection to verify locations using the geopy package.

# Script Descriptions

01_data_collection.py
Parses the watch-history.html file to extract video titles, URLs, channel names, and timestamps, saving the data to watch_history.csv.

02_data_preprocessing.py
Processes watch_history.csv to ensure proper encoding, filter out unavailable videos, and reformat date and time columns. Saves the processed data to watch_history_processed.csv.

03_nlp_analysis.py
Performs natural language processing (NLP) on video titles to generate unigrams, bigrams, and trigrams. Extracts named entities (locations) and maps them to states and countries. Saves the processed data to watch_history_nlp.csv.

04_lda_analysis.py
Uses Latent Dirichlet Allocation (LDA) to analyze common title tokens in the form of unigrams, bigrams, and trigrams. Ensures tokens appear in at least two distinct videos before inclusion. Saves results to lda_topics_by_quarter.csv.

05_active_periods_analysis.py
Analyzes peak watching months and most active hours in each quarter. Caps outliers using the IQR method and fills in missing data points with zeros. Saves results to peak_watching_months.csv, most_active_hours_by_quarter.csv, and top_30_youtubers.csv.

city names converter.py (Bonus)
Converts city names to states using the geopy package. Requires an internet connection. Outputs city_state_mapping.csv.

# Notes
Ensure all dependencies are installed.
Maintain the directory structure for smooth operation.
Follow the order of script execution to avoid errors.

# Acknowledgements
Special thanks to all contributors and open-source libraries used in this project.
=======
# GoogleTakeout
Python scripts to analyze YouTube watch history data, utilizing NLP, LDA, and data visualization tools for insights.
>>>>>>> origin/main
