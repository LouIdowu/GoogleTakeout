#this script analyzes the processed dataset and uses ai to get additional insights
#it uses natural langauge toolkit to analyze video titles for tokens.
#tokens in this case are basically the most important parts of a sentence.
#it scans every video title for locations.
#it then utilizes two mapping csvs already included in the project zip to match known cities to their corresponding us state or country
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.util import ngrams
from collections import Counter
import os
import stanza

#ensure necessary NLTK data packages are downloaded
nltk.download('punkt')
nltk.download('stopwords')

#initializes Stanza pipeline
stanza.download('en')
nlp = stanza.Pipeline('en', processors='tokenize,ner')

#defines the project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_CSV_PATH = os.path.join(PROJECT_DIR, 'history', 'watch_history_processed.csv')
CITY_STATE_CSV_PATH = os.path.join(PROJECT_DIR, 'history', 'city_state_mapping.csv')
CITY_COUNTRY_CSV_PATH = os.path.join(PROJECT_DIR, 'history', 'citiestocountries.csv')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'history', 'quarterly_reports')

#load in processed data
df = pd.read_csv(PROCESSED_CSV_PATH, encoding='utf-8')

#load city-state and city-country mappings
#while doing this project, i had troubles with false positives getting reported as locations with the stanza.
#it kept incorrectly flagging non-locations as locations
#to fix this, i utilized a csv of several hundred of the worlds most popular locations to prevent this
city_state_mapping = pd.read_csv(CITY_STATE_CSV_PATH)
city_country_mapping = pd.read_csv(CITY_COUNTRY_CSV_PATH)

#convert city mappings to dictionaries
city_to_state = dict(zip(city_state_mapping['City'], city_state_mapping['State']))
city_to_country = dict(zip(city_country_mapping['City'], city_country_mapping['Country']))

#define stopwords
stop_words = set(stopwords.words('english'))

#tokenize video titles and remove stopwords, then generate unigrams, bigrams, and trigrams
#unigrams, bigrams and trigrams are basically one word, two word phrases, and three word phrases.
def process_title(title):
    tokens = word_tokenize(title.lower())
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    unigrams = filtered_tokens
    bigrams = [' '.join(gram) for gram in ngrams(filtered_tokens, 2)]
    trigrams = [' '.join(gram) for gram in ngrams(filtered_tokens, 3)]
    return unigrams + bigrams + trigrams

df['Title Tokens'] = df['Video Title'].apply(process_title)

# function to get quarter
def get_quarter(month):
    if month in [1, 2, 3]:
        return 'Q1'
    elif month in [4, 5, 6]:
        return 'Q2'
    elif month in [7, 8, 9]:
        return 'Q3'
    else:
        return 'Q4'

df['Quarter'] = df['Date'].apply(lambda x: get_quarter(pd.to_datetime(x).month))

#extract named entities (locations)
def extract_locations(title):
    doc = nlp(title)
    locations = [ent.text for ent in doc.entities if ent.type in ['GPE', 'LOC']]
    return locations

df['Locations'] = df['Video Title'].apply(extract_locations)

# function to map locations to states and countries
def map_locations(location_list):
    states, countries = [], []
    if location_list and location_list != '[]':
        for location in location_list:
            state = city_to_state.get(location)
            country = city_to_country.get(location)
            if state:
                states.append(state)
            if country:
                countries.append(country)
            if not state and not country:
                if location in city_state_mapping['State'].values:
                    states.append(location)
                elif location in city_country_mapping['Country'].values:
                    countries.append(location)
    return ', '.join(states), ', '.join(countries)

df['State'], df['Country'] = zip(*df['Locations'].apply(map_locations))

#drop the 'Locations' column
#if anything was added to the locations column, it should automatically get added to either the state column or the country column using the mapping.
#by dropping the locations column, all "locations" that didnt get added to either get removed thus fixing the problem of false positives
df.drop(columns=['Locations'], inplace=True)

#create a directory for quarterly reports if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

#analyze each quarter
for year in df['Date'].apply(lambda x: pd.to_datetime(x).year).unique():
    for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
        quarter_df = df[(df['Date'].apply(lambda x: pd.to_datetime(x).year) == year) & (df['Quarter'] == quarter)]
        if not quarter_df.empty:
            all_tokens = [token for sublist in quarter_df['Title Tokens'] for token in sublist]
            common_keywords = Counter(all_tokens).most_common(10)

            # Save quarterly analysis
            with open(os.path.join(OUTPUT_DIR, f'{year}_{quarter}_common_keywords.txt'), 'w', encoding='utf-8') as f:
                for keyword, count in common_keywords:
                    f.write(f"{keyword}: {count}\n")

            print(f"{year} {quarter} analysis complete. Results saved in '{year}_{quarter}_common_keywords.txt'.")

#save processed data with tokens and entities
df.to_csv(os.path.join(PROJECT_DIR, 'history', 'watch_history_nlp.csv'), index=False, encoding='utf-8-sig')

print("NLP analysis complete. Processed file saved as 'watch_history_nlp.csv'.")
