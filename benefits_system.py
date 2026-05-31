import pandas as pd
import numpy as np
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:Cheese_cake218@localhost/benefits_system")

# Load data
df = pd.read_sql("SELECT * FROM benefits_applications", engine)
targets = pd.read_sql("SELECT * FROM stage_targets_benefits", engine)


#PW1. Number each stage per application in time order — same as W1.
#stage_number = df.sort_values(['application_id', 'entered_at']).groupby('application_id').cumcount() + 1
#print(stage_number)

#PW2. For each application show current stage and previous stage side by side.
#df_sorted = df.sort_values(['application_id', 'entered_at'])
#df_sorted['previous_stage'] = df_sorted.groupby('application_id')['stage'].shift(1)
#print(df_sorted[['application_id', 'stage', 'previous_stage']])

#PW3. For each application show current stage and next stage side by side.
#df_sorted = df.sort_values(['application_id', 'entered_at'])
#df_sorted['next_stage'] = df_sorted.groupby('application_id')['stage'].shift(-1)
#print(df_sorted[['application_id', 'stage', 'next_stage']])

# PW4. Days between each stage
df_sorted = df.sort_values(['application_id', 'entered_at'])
df_sorted['days_in_stage'] = df_sorted.groupby('application_id')['entered_at'].diff().dt.days
print(df_sorted[['application_id', 'stage', 'entered_at', 'days_in_stage']])

# PW5. Rank applications by total duration
total_duration = df.groupby('application_id')['entered_at'].agg(['min', 'max']).reset_index()
total_duration['total_days'] = (total_duration['max'] - total_duration['min']).dt.days
total_duration['ranking'] = total_duration['total_days'].rank(ascending=False, method='dense')
print(total_duration.sort_values('ranking'))

# PW6. Rank within each applicant type
total_duration = df.groupby(['application_id', 'applicant_type'])['entered_at'].agg(['min', 'max']).reset_index()
total_duration['total_days'] = (total_duration['max'] - total_duration['min']).dt.days
total_duration['ranking'] = total_duration.groupby('applicant_type')['total_days'].rank(ascending=False, method='dense')
print(total_duration.sort_values(['applicant_type', 'ranking']))

# PW7. Caseworker ranking by application count
caseworker = df.groupby('assigned_to')['application_id'].nunique().reset_index()
caseworker.columns = ['assigned_to', 'num_apps']
caseworker['ranking'] = caseworker['num_apps'].rank(ascending=False, method='dense')
print(caseworker.sort_values('ranking'))

# PW8. Running total per stage over time
df['date'] = df['entered_at'].dt.date
daily = df.groupby(['stage', 'date'])['application_id'].count().reset_index()
daily.columns = ['stage', 'date', 'daily_count']
daily['running_total'] = daily.groupby('stage')['daily_count'].cumsum()
print(daily)

#PD9. For each applicant_type show total applications, approved count, denied count and approval rate — all in one dataframe.

#long version
#decisions = df[df['stage'] == 'Approval']

# total apps per type
#total = decisions.groupby('applicant_type')['application_id'].nunique().reset_index()
#total.columns = ['applicant_type', 'total_apps']

# approved per type
#approved = decisions[decisions['status'] == 'Approved'].groupby('applicant_type')['application_id'].nunique().reset_index()
#approved.columns = ['applicant_type', 'approved']

# denied per type
#denied = decisions[decisions['status'] == 'Denied'].groupby('applicant_type')['application_id'].nunique().reset_index()
#denied.columns = ['applicant_type', 'denied']

# merge all together
#result = total.merge(approved, on='applicant_type').merge(denied, on='applicant_type')
#result['approval_rate'] = round(result['approved'] / result['total_apps'] * 100, 1)
#print(result)

#PD10. Export your PD9 result to a CSV called approval_rates.csv.
#result.to_csv('approval_rates.csv', index=False)

#short version using lambda
'''
decisions = df[df['stage'] == 'Approval']

result = decisions.groupby('applicant_type').agg(
    total_apps=('application_id', 'nunique'),
    approved=('status', lambda x: (x == 'Approved').sum()),
    denied=('status', lambda x: (x == 'Denied').sum())
).reset_index()

result['approval_rate'] = round(result['approved'] / result['total_apps'] * 100, 1)

print(result)
'''

#PD8. Find all applications that never reached Benefits Issued.
#completed = df[df['stage'] == 'Benefits Issued']['application_id'].unique()
#incomplete = df[~df['application_id'].isin(completed)]
#print(incomplete['application_id'].nunique())

#PD7. For each stage show the average days_in_stage — you'll need to calculate days_in_stage first.
#df['days_in_stage'] = df.groupby('application_id')['entered_at'].diff().dt.days
#avg = df.groupby('stage')['days_in_stage'].mean().round(1)
#print(avg)

#PD6. Add a new column called is_approved — 1 if status is Approved, 0 if not.
#df['is_approved'] = np.where(df['status'] == 'Approved', 1, 0)
#print(df)

#PD5. Filter to applications that are either Urgent or Critical priority — how many rows?
#urg_crit_prior = df[df['priority'].isin(['Urgent', 'Critical'])]
#print(len(urg_crit_prior))

#PD4. Show the count of each applicant_type sorted highest to lowest.
#count_applicant_type = df.groupby('applicant_type')['application_id'].nunique().sort_values(ascending=False)
#print(count_applicant_type)

#critical_priority = df[df['priority'] == 'Critical']['application_id'].nunique()
#print(critical_priority)



#total_cases = df.groupby('stage')['application_id'].nunique().reset_index()
#total_cases.columns = ['stage', 'total_cases']
#
#last_stage = df.sort_values('entered_at').groupby('application_id').last().reset_index()
#stuck = last_stage[last_stage['stage'] != 'Benefits Issued']
#stuck_cases = stuck.groupby('stage')['application_id'].count().reset_index()
#stuck_cases.columns = ['stage', 'stuck_cases']
#
#df['days_in_stage'] = df.sort_values(['application_id', 'entered_at']).groupby('application_id')['entered_at'].diff().dt.days
#df['days_in_stage'] = df['days_in_stage'].clip(lower=0)
#avg_days = df.groupby('stage')['days_in_stage'].mean().round(1).reset_index()
#avg_days.columns = ['stage', 'avg_days']
#
#merged_df = total_cases.merge(stuck_cases, on='stage', how='outer').merge(avg_days, on='stage', how='outer')
#merged_df = merged_df.merge(targets, on='stage')
#merged_df['status'] = np.where(merged_df['avg_days'] > merged_df['target_days'], 'Over', 'On Track')
#
#merged_df = merged_df.fillna(0)
#print(merged_df)

