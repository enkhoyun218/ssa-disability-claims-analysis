import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# Connect to MySQL
engine = create_engine("mysql+pymysql://root:Cheese_cake218@localhost/case_pipeline")

# Pull ALL data into a dataframe
df = pd.read_sql("SELECT * FROM case_events", engine)

# ---- EXPLORE THE DATA ----

#P16. Show the drop off rate per case type as a percentage.
#P17. Recreate the staff leaderboard from A8 — total cases, closed cases, open cases, closure rate — all in one dataframe.





#For each case type + stage combination show:
#
#How many cases passed through
#How many are stuck there right now
#Average days spent

#total_cases = df.groupby(['case_type', 'stage'])['case_id'].nunique().reset_index()
#total_cases.columns = ['case_type', 'stage', 'total_cases']
#
#closed_id = df[df['stage'] == 'Closed']['case_id'].unique()
#stuck_cases = df[~df['case_id'].isin(closed_id)].groupby(['case_type', 'stage'])['case_id'].nunique().reset_index()
#stuck_cases.columns = ['case_type', 'stage', 'stuck_cases']
#
#df['days_in_stage'] = df.groupby('case_id')['entered_at'].diff().dt.days
#avg_days = df.groupby(['case_type', 'stage'])['days_in_stage'].mean().round(1).reset_index()
#avg_days.columns = ['case_type', 'stage', 'avg_days']
#
#merge_df = total_cases.merge(stuck_cases, on=['case_type', 'stage'], how='outer').merge(avg_days, on=['case_type', 'stage'], how='outer')
#merge_df = merge_df.fillna(0)
#print(merge_df)


#PP4. For each stage show:
#
#Fastest case ever through that stage (min days)
#Slowest case ever through that stage (max days)
#Average days
#How many cases exceeded 15 days in that stage

#df['days_in_stage'] = df.groupby('case_id')['entered_at'].diff().dt.days
#
#basic_calc = df.groupby('stage')['days_in_stage'].agg(['min', 'max', 'mean']).reset_index()
#basic_calc.columns = ['stage', 'min', 'max', 'mean']
#
#exceeded = df[df['days_in_stage'] > 15].groupby('stage')['case_id'].count().reset_index()
#exceeded.columns = ['stage', 'exceeded']
#
#merged_df = basic_calc.merge(exceeded, on='stage', how='outer')
#merged_df = merged_df.fillna(0)
#print(merged_df)


#PP3. For each month show:
#
#New cases opened (first Intake event that month)
#Cases closed that month
#Difference between opened and closed

#df['month'] = df['entered_at'].dt.to_period('M')
#
#new_cases = (df[df['stage'] == 'Intake'].groupby('month')['case_id'].nunique().reset_index())
#new_cases.columns = ['month', 'new_cases']
#
#old_cases = (df[df['stage'] == 'Closed'].groupby('month')['case_id'].nunique().reset_index())
#old_cases.columns = ['month', 'old_cases']
#
#merged_df = new_cases.merge(old_cases, on='month', how='outer')
#merged_df = merged_df.fillna(0)
#merged_df['diff'] = merged_df['new_cases'] - merged_df['old_cases']
#print(merged_df)


#PP2. For each staff member show:
#
#Total cases handled
#Average days per stage across all their cases
#Number of cases currently open
#
#All in one dataframe.

#total_cases = df.groupby('assigned_to')['case_id'].nunique().reset_index()
#total_cases.columns = ['assigned_to', 'total_cases']
#
#df['days_in_stage'] = df.groupby('case_id')['entered_at'].diff().dt.days
#avg_days = df.groupby('assigned_to')['days_in_stage'].mean().round(1).reset_index()
#avg_days.columns = ['assigned_to', 'avg_days']
#
#closed_id = df[df['stage'] == 'Closed']['case_id'].unique()
#open_cases = df[~df['case_id'].isin(closed_id)].groupby('assigned_to')['case_id'].nunique().reset_index()
#open_cases.columns = ['assigned_to', 'stuck_cases']
#
#merge_df = total_cases.merge(open_cases, on='assigned_to').merge(avg_days, on='assigned_to')
#print(merge_df)



#PP1. For each case type show:
#
#Total cases
#Cases that reached Closed
#Cases that never reached Closed
#Closure rate as a percentage
#
#All in one dataframe.

#total_cases = df.groupby('case_type')['case_id'].nunique().reset_index()
#total_cases.columns = ['case_type', 'total_cases']
#
#closed_cases = df[df['stage'] == 'Closed'].groupby('case_type')['case_id'].nunique().reset_index()
#closed_cases.columns = ['case_type', 'closed_cases']
#
#closed_id = df[df['stage'] == 'Closed']['case_id'].unique()
#stuck_cases = df[~df['case_id'].isin(closed_id)].groupby('case_type')['case_id'].nunique().reset_index()
#stuck_cases.columns = ['case_type', 'stuck_cases']
#
#merge_df = total_cases.merge(closed_cases, on='case_type').merge(stuck_cases, on='case_type')
#
#merge_df['closure_rate'] = round((merge_df['closed_cases'] / merge_df['total_cases']) * 100.0, 1)
#print(merge_df)


#P15. Recreate your M8 dashboard in pandas — for each stage show total cases, stuck cases, and average days spent.

total_cases = df.groupby('stage')['case_id'].nunique().reset_index()
total_cases.columns = ['stage', 'total_cases']

last_stage = df.sort_values('entered_at').groupby('case_id').last().reset_index()
stuck = last_stage[last_stage['stage'] != 'Closed']
stuck_cases = stuck.groupby('stage')['case_id'].count().reset_index()
stuck_cases.columns = ['stage', 'stuck_cases']

df['days_in_stage'] = df.sort_values(['case_id', 'entered_at']).groupby('case_id')['entered_at'].diff().dt.days
df['days_in_stage'] = df['days_in_stage'].clip(lower=0)
avg_days = df.groupby('stage')['days_in_stage'].mean().round(1).reset_index()
avg_days.columns = ['stage', 'avg_days']
merged_df = total_cases.merge(stuck_cases, on='stage', how='outer').merge(avg_days, on='stage', how='outer')
targets = pd.read_sql("SELECT * FROM stage_targets", engine)
merged_df = merged_df.merge(targets, on='stage')
merged_df['status'] = np.where(merged_df['avg_days'] > merged_df['target_days'], 'Over', 'On Track')

merged_df = merged_df.fillna(0)
print(merged_df)

merged_df.to_csv('pipeline_dashboard.csv', index=False)

#P11. Add a new column called month that extracts the month from entered_at.
#df['month'] = df['entered_at'].dt.month
#print(df['month'])


#P12. How many events happened per month? Sort chronologically.
#df['month'] = df['entered_at'].dt.month
#events_per_month = df.groupby('month')['case_id'].count().sort_index()
#print(events_per_month)


#P13. Calculate the time difference between consecutive events per case — add it as a new column called days_in_stage.
#df['days_in_stage'] = df.groupby('case_id')['entered_at'].diff().dt.days
#print(df['days_in_stage'])


#P14. Which cases have been in their current stage for more than 20 days?
#df['days_in_stage'] = df.groupby('case_id')['entered_at'].diff().dt.days
#stuck = df[df['days_in_stage'] > 20]
#print(stuck[['case_id', 'stage', 'days_in_stage']])


#P6. How many unique cases never reached Closed?
#closed_cases = df[df['stage'] == 'Closed']['case_id'].unique()
#open_cases = df[~df['case_id'].isin(closed_cases)]
#print(f'There are {open_cases['case_id'].nunique()} open cases.')


#P7. Show the count of cases per stage — sorted by count descending.
#cases_per_stage = df.groupby('stage')['case_id'].nunique().sort_values(ascending=False)
#print(cases_per_stage)


#P8. Filter to only Appeal and Permit case types combined — how many rows?
#appeal_permit = df[df['case_type'].isin(['Appeal', 'Permit'])]
#print(len(appeal_permit))


#P9. Add a new column called is_closed — 1 if stage is Closed, 0 if not.
#df['is_closed'] = np.where(df['stage'] == 'Closed', 1, 0)
#print(df[['stage', 'is_closed']].head(10))


#P10. Which staff member has the most events assigned to them?
#staff_case_count = df.groupby('assigned_to')['case_id'].count().sort_values(ascending=False)
#print(staff_case_count.head(1))


#P1. How many unique case types are there and what are they?
#case_type_count = df['case_type'].nunique()
#case_types = df['case_type'].unique()
#print(f"There are {case_type_count} unique case types, which are {case_types}")


#P2. How many cases are assigned to each staff member? Sort highest to lowest.
#print(df.groupby('assigned_to')['case_id'].nunique().sort_values(ascending=False))


#P3. Filter the dataframe to only show Verification stage rows — how many are there?
#verification = df[df['stage'] == 'Verification']
#print(verification)
#print(f"There are {len(verification)} rows in the verification stage.")


#P4. Show all events for case_id = 5 sorted by entered_at.
#case_5 = df[df['case_id'] == 5].sort_values('entered_at')
#print(case_5)


#P5. What is the earliest and latest entered_at date in the dataset?
#earliest = df['entered_at'].min()
#latest = df['entered_at'].max()
#print(f'earliest_date = {earliest} and latest_date = {latest}')

"""
# P1. How many rows and columns?
print(df.shape)

# P2. What are the column names and data types?
print(df.dtypes)

# P3. First 5 rows
print(df.head())

# P4. Basic stats
print(df.describe())

# P5. Unique stages (same as SELECT DISTINCT stage)
print(df['stage'].unique())

# P6. Count of each case type (same as GROUP BY case_type)
print(df['case_type'].value_counts())

# P7. Filter to only Verification stage (same as WHERE stage = 'Verification')
verification = df[df['stage'] == 'Verification']
print(verification.shape)

# P8. Filter to only case_id = 1
case_1 = df[df['case_id'] == 1].sort_values('entered_at')
print(case_1)

# P9. How many unique cases? (same as COUNT DISTINCT case_id)
print(df['case_id'].nunique())

# P10. Cases that never reached Closed
closed_ids = df[df['stage'] == 'Closed']['case_id'].unique()
open_cases = df[~df['case_id'].isin(closed_ids)]
print(f"Open cases: {open_cases['case_id'].nunique()}")

df.groupby('case_type')['case_id'].nunique().sort_values(ascending=False)
"""