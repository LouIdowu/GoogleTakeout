#this script reads in the watch history html file and scrapes it.
#it uses beautifulsoup to parse through the html file.
#it uses pandas to add parsed information into a dataframe then saves it as a csv.
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os

#define the project directory. designed to work relative as long as the html is in the right place.
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE_PATH = os.path.join(PROJECT_DIR, 'history', 'watch-history.html')
CSV_OUTPUT_PATH = os.path.join(PROJECT_DIR, 'history', 'watch_history.csv')

#uses utf 8 encoding.this ensures non latin characters, emojis and symbols display just fine
#was using the latin 1 encoding at first and many different characters in youtube titles fall outside of these ranges
#this actually gave me a lot of trouble as diagnosing why the non latin characters looked so weird was hard
def load_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

#uses beautifulsoup to parse through html file.
def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    records = []

    #for loop through the HTML content
    for entry in soup.find_all('div', class_='outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp'):
        title_element = entry.find('a')
        channel_element = entry.find_all('a')[1] if len(entry.find_all('a')) > 1 else None
        date_time_element = entry.find('div', class_='content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1')

        title = title_element.text if title_element else 'No title'
        url = title_element['href'] if title_element else 'No URL'
        channel = channel_element.text if channel_element else 'No channel'
        channel_url = channel_element['href'] if channel_element else 'No URL'
        date_time_raw = date_time_element.contents[-1].strip() if date_time_element else 'No date_time'

        # Remove unwanted characters and prefix
        date_time_raw = date_time_raw.replace('Watched', '').strip()
        date_time_str = date_time_raw.rsplit(' ', 1)[0]

        # Parse the date and time
        try:
            date_time_obj = datetime.strptime(date_time_str, '%b %d, %Y, %I:%M:%S %p')
            date = date_time_obj.strftime('%d-%b-%Y')
            time = date_time_obj.strftime('%H:%M:%S')
        except ValueError as e:
            print(f"Error parsing date-time: {e}")
            date = 'Invalid date'
            time = 'Invalid time'

        records.append({
            'Video Title': title,
            'URL': url,
            'Channel Name': channel,
            'Channel URL': channel_url,
            'Date': date,
            'Time': time,
        })

    return records


def save_to_dataframe(records):
    df = pd.DataFrame(records)
    # Save the DataFrame with UTF-8 encoding
    df.to_csv(CSV_OUTPUT_PATH, index=False, encoding='utf-8-sig')
    return df
#saves it to pandas dataframe

def main():
    html_content = load_html(HTML_FILE_PATH)
    records = parse_html(html_content)
    df = save_to_dataframe(records)
    print(df.head())  #just for quick verification, remove or comment out in production


if __name__ == '__main__':
    main()
