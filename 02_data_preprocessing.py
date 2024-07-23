#this script cleans through the raw data that was created in the last script
#some youtube videos are created by terminated, suspended channels.
#a video may also just be privated.
# these have no real records to them and arent useful to us so its best to just remove them.
import pandas as pd
import os

#define the project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_CSV_PATH = os.path.join(PROJECT_DIR, 'history', 'watch_history.csv')
PROCESSED_CSV_PATH = os.path.join(PROJECT_DIR, 'history', 'watch_history_processed.csv')

#ensure proper encoding for non-Latin characters using UTF-8
def ensure_utf8(text):
    try:
        return text.encode('utf-8').decode('utf-8')
    except UnicodeEncodeError:
        return text

def preprocess_data():
    #load in the raw data file
    df = pd.read_csv(RAW_CSV_PATH, encoding='utf-8')

    #utf 8 encoding
    df['Video Title'] = df['Video Title'].apply(lambda x: ensure_utf8(x) if isinstance(x, str) else x)
    df['Channel Name'] = df['Channel Name'].apply(lambda x: ensure_utf8(x) if isinstance(x, str) else x)

    #filter out the unavailable videos
    df = df[~((df['Channel Name'] == 'here') & (df['Channel URL'] == 'https://myaccount.google.com/activitycontrols'))]

    #preprocess data
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)
    df.dropna(subset=['Date'], inplace=True)  # Remove rows with invalid dates

    #convert date to desired format with 4-digit year
    #tableau prefers data to be dd-MMM-yyyy so thats what well be using.
    df['Date'] = df['Date'].apply(lambda x: x.strftime('%d-%b-%Y') if pd.notnull(x) else x)
    df['Date'] = df['Date'].apply(lambda x: x[:-2] + "" + x[-2:])  # Add "20" before the last two digits

    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.strftime('%H:%M:%S')

    #save processed data in a new csv
    df.to_csv(PROCESSED_CSV_PATH, index=False, encoding='utf-8-sig')
    print("Data preprocessing complete. Processed file saved as 'watch_history_processed.csv'.")

if __name__ == '__main__':
    preprocess_data()
