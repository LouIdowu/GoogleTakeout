#this script analyzes the process data we created in the second version. it does not use the nlp version as we only need the processed data for this.
#it takes the processed data in, then creates insights four our peak watching months, most active hours by quarter, and top 30 YouTubers
#it is important to make sure that this is done in a way that tableau likes to make the data visualization process easier
#in this script, i use the phrase "watchtime" a lot. this simply refers to number of videos clicked on, regardless of how long i watched them or even at all
#youtube does not report watchtime for each video in this dataset so number of clicked on videos will be "watchtime".

import pandas as pd
import os
import calendar

# define the project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_CSV_PATH = os.path.join(PROJECT_DIR, 'history', 'watch_history_processed.csv')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'history', 'insights')

#load in the processed data
df = pd.read_csv(PROCESSED_CSV_PATH, encoding='utf-8')

#ensure the 'Date' and 'Time' columns are in the correct datetime format
df['Date'] = pd.to_datetime(df['Date'])
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time

#peak Watching Months
df['Month'] = df['Date'].dt.month
df['Year'] = df['Date'].dt.year

#generate all possible Year-Month combinations within the date range
all_months = pd.date_range(start=df['Date'].min().to_period('M').to_timestamp(), end=df['Date'].max().to_period('M').to_timestamp(), freq='M')
all_months_df = pd.DataFrame([(date.year, date.month) for date in all_months], columns=['Year', 'Month'])

#group by Year and Month and fill missing months with zeros
#it is important to have missing zeroes in this case. otherwise, the script would just skip over time periods with no activity.
#this is bad especially in the data visualization phase because those skipped values will cause discontinuities
#most data visualization softwares cant handle them so its best to represent those periods with no watchtime as zeroes rather than skipping.
monthly_watchtime = df.groupby(['Year', 'Month']).size().reset_index(name='Total Watchtime')
monthly_watchtime = all_months_df.merge(monthly_watchtime, on=['Year', 'Month'], how='left').fillna(0)

#cap outliers using IQR method
#sometimes I would leave youtube autoplay on while going to sleep, causing outliers in watched videos.
#it is important to cap those outliers as they can deceivingly skew the data in the data visualization phase.
#this is standard in the field of statistics as data science.
Q1 = monthly_watchtime['Total Watchtime'].quantile(0.25)
Q3 = monthly_watchtime['Total Watchtime'].quantile(0.75)
IQR = Q3 - Q1
upper_bound = Q3 + 1.5 * IQR

monthly_watchtime['Total Watchtime'] = monthly_watchtime['Total Watchtime'].apply(lambda x: min(x, upper_bound))

#round 'Total Watchtime' to the nearest integer
monthly_watchtime['Total Watchtime'] = monthly_watchtime['Total Watchtime'].round().astype(int)

#replace numeric month values with full month names to ensure readability and user friendlieness
monthly_watchtime['Month'] = monthly_watchtime['Month'].apply(lambda x: calendar.month_name[x])

#save peak watching months to CSV
os.makedirs(OUTPUT_DIR, exist_ok=True)
monthly_watchtime.to_csv(os.path.join(OUTPUT_DIR, 'peak_watching_months.csv'), index=False, encoding='utf-8-sig')

#most Active Hours in Each Quarter
def get_quarter(month):
    if month in [1, 2, 3]:
        return 'Q1'
    elif month in [4, 5, 6]:
        return 'Q2'
    elif month in [7, 8, 9]:
        return 'Q3'
    else:
        return 'Q4'

df['Quarter'] = df['Date'].dt.month.apply(get_quarter)
df['Hour'] = df['Time'].apply(lambda x: x.hour)

#create a DataFrame with all combinations of Year, Quarter, and Hour
years = df['Year'].unique()
quarters = df['Quarter'].unique()
hours = list(range(0, 24))

all_combinations = pd.MultiIndex.from_product([years, quarters, hours], names=['Year', 'Quarter', 'Hour'])
all_combinations_df = pd.DataFrame(index=all_combinations).reset_index()

#merge with the original data to fill in missing hours with zeros
#missing zeroes are important for the same reasons commented above.
quarterly_active_hours = df.groupby(['Year', 'Quarter', 'Hour']).size().reset_index(name='Total Watchtime')
merged_df = pd.merge(all_combinations_df, quarterly_active_hours, on=['Year', 'Quarter', 'Hour'], how='left').fillna(0)

#generate a date for each row based on the year and quarter
def generate_date(year, quarter):
    if quarter == 'Q1':
        return f'01-Jan-{year}'
    elif quarter == 'Q2':
        return f'01-Apr-{year}'
    elif quarter == 'Q3':
        return f'01-Jul-{year}'
    elif quarter == 'Q4':
        return f'01-Oct-{year}'
#placeholder dates that wont be present in the data visualization phase. tableau just likes to have them so well plug in estimates.
merged_df['Date'] = merged_df.apply(lambda row: generate_date(row['Year'], row['Quarter']), axis=1)

#cap the outliers in 'Total Watchtime'
#capped outliers are important for the same reasons referenced above.
Q1 = merged_df['Total Watchtime'].quantile(0.25)
Q3 = merged_df['Total Watchtime'].quantile(0.75)
IQR = Q3 - Q1
upper_bound = Q3 + 1.5 * IQR

merged_df['Total Watchtime'] = merged_df['Total Watchtime'].apply(lambda x: min(x, upper_bound))

#save the updated data to a new CSV file
output_path = os.path.join(OUTPUT_DIR, 'most_active_hours_by_quarter_filled_capped.csv')
merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')

#top 30 Most Watched YouTubers
#creating a dataframe for youtubers watched the most.
top_youtubers = df['Channel Name'].value_counts().head(30).reset_index()
top_youtubers.columns = ['Channel Name', 'Watch Count']

#save top 30 most watched YouTubers to CSV
top_youtubers.to_csv(os.path.join(OUTPUT_DIR, 'top_30_youtubers.csv'), index=False, encoding='utf-8-sig')

print("Peak watching months, most active hours by quarter, and top 30 YouTubers analysis complete. CSV files saved.")
