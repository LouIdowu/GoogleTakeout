#this script utilizes latent dirichlet allocation to parse tokens for common themes or trends.
#it makes use of unigrams, bigrams, and trigrams. (one word, two word phrases, and three word phrases)
#the script also filters out video topics that are only watched once.
#that way if i watch one video many times, it does not report associated topics as a trend.
#this prevents flukes and outliers

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from collections import defaultdict
import os

#define the project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
NLP_CSV_PATH = os.path.join(PROJECT_DIR, 'history', 'watch_history_nlp.csv')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'history', 'lda_analysis_by_quarter')

#load the data with tokens
df = pd.read_csv(NLP_CSV_PATH, encoding='utf-8')

#combine tokens into a single string for each video title
df['Title Tokens Combined'] = df['Title Tokens'].apply(lambda x: ' '.join(eval(x)))

#initialize CountVectorizer with increased minimum document frequency to reduce sensitivity
#if you want more topics outputted, increase sensitivity. if you want only the ones with the highest frequency, decrease it.
vectorizer = CountVectorizer(min_df=0.027, ngram_range=(1, 3))  # adjust min_df to increase/decrease sensitivity

#initialize LDA
n_topics = 5  # change n_topics as needed
lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)


#function to display topics
def display_topics(model, feature_names, no_top_words):
    topics = {}
    for topic_idx, topic in enumerate(model.components_):
        topics[f'Topic {topic_idx + 1}'] = [feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]
    return topics


#helper function to get unique video URLs per token
#this prevents video topics that are watched ust once from appearing
#if i watch a video with a unique topic just one time, it is reported along with other video topics that span over several different videos
#that is not indicative of a trend, and can be considered an outlier. so for that reason it is good to filter out these flukes.
def get_unique_video_urls_per_token(token, tokens_column, urls_column):
    unique_urls = set()
    for tokens, url in zip(tokens_column, urls_column):
        if token in eval(tokens):
            unique_urls.add(url)
    return unique_urls


#filter out numerical-only tokens. digits are not insightful in this case.
# if they are part of a trigram then bigram then thats ok but otherwise it is best to delete them
def filter_numerical_tokens(tokens):
    return [token for token in tokens if not token.isdigit()]


#create a directory for LDA analysis if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

#analyze each quarter
lda_results = []
for year in df['Date'].apply(lambda x: pd.to_datetime(x).year).unique():
    yearly_df = df[pd.to_datetime(df['Date']).dt.year == year]
    for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
        quarter_df = df[(pd.to_datetime(df['Date']).dt.year == year) & (df['Quarter'] == quarter)]
        if not quarter_df.empty:
            token_matrix = vectorizer.fit_transform(quarter_df['Title Tokens Combined'])
            lda.fit(token_matrix)
            feature_names = vectorizer.get_feature_names_out()
            topics = display_topics(lda, feature_names, no_top_words=10)

            for words in topics.values():
                for word in words:
                    if not word.isdigit():  # Skip numerical-only tokens
                        unique_urls = get_unique_video_urls_per_token(word, yearly_df['Title Tokens'], yearly_df['URL'])
                        if len(unique_urls) >= 2:  # Ensure the token appears in at least 2 distinct video URLs within the year
                            word_count = quarter_df['Title Tokens Combined'].str.count(word).sum()
                            lda_results.append({
                                'Year': year,
                                'Date': pd.to_datetime(quarter_df['Date']).dt.strftime('%m %d %Y').unique()[0],
                                # Ensure date format
                                'Quarter': quarter,
                                'Word': word,
                                'Frequency': word_count
                            })

#remove duplicates
lda_results_df = pd.DataFrame(lda_results).drop_duplicates()

#save LDA results to CSV
lda_results_df.to_csv(os.path.join(OUTPUT_DIR, 'lda_topics_by_quarter.csv'), index=False, encoding='utf-8-sig')

print("LDA analysis complete. Topics by quarter saved in 'lda_topics_by_quarter.csv'.")
