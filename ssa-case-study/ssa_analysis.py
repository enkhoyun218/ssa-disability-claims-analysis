import pandas as pd
import numpy as np

# ============================================================
# SSA Disability Claims Analysis
# Data: SSA State Agency Monthly Workload Data
# Source: https://www.ssa.gov/disability/data/ssa-sa-mowl.htm
# ============================================================

# --- LOAD & CLEAN DATA ---

df = pd.read_csv('SSA-SA-MOWL.csv', low_memory=False)

# Convert all numeric columns upfront
non_numeric = ['File Name', 'Update Date', 'Region Code',
               'State Code', 'Date Type', 'Date',
               'Formatted Date', 'Prototype State']

for col in df.columns:
    if col not in non_numeric:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(',', ''),
            errors='coerce'
        )

df['Date'] = pd.to_datetime(df['Date'])

# Filter to US states only
us_states = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA',
             'HI','ID','IL','IN','IA','KS','KY','LA','ME','MD',
             'MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
             'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC',
             'SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','DC']

state_df = df[df['State Code'].isin(us_states)].copy()
latest = state_df[state_df['Date'] == state_df['Date'].max()].copy()

print(f"Data loaded — shape: {df.shape}, latest date: {state_df['Date'].max().date()}")


# ============================================================
# PROBLEM 1: Which states have the worst backlog?
# ============================================================

print("\n--- P1: Top 10 States by Backlog ---")
backlog = latest[['State Code', 'Closing Pending (All Initial)']]\
    .sort_values('Closing Pending (All Initial)', ascending=False)\
    .head(10)
print(backlog.to_string(index=False))


# ============================================================
# PROBLEM 2: Are states keeping up with incoming claims?
# (Receipts vs Determinations gap)
# ============================================================

print("\n--- P2: Top 10 States by Intake vs Processing Gap ---")
latest['gap'] = latest['Receipts (All Initial)'] - latest['Determinations (All Initial)']
latest['processing_rate_pct'] = round(
    latest['Determinations (All Initial)'] / latest['Receipts (All Initial)'] * 100, 1
)

gap_result = latest[['State Code', 'Receipts (All Initial)',
                      'Determinations (All Initial)', 'gap', 'processing_rate_pct']]\
    .sort_values('gap', ascending=False)\
    .head(10)
print(gap_result.to_string(index=False))


# ============================================================
# PROBLEM 3: Is the national approval rate improving over time?
# ============================================================

print("\n--- P3: National Allowance Rate Trend (last 20 months) ---")
trend = state_df.groupby('Date')['Allowance Rate (All Initial)']\
    .mean().round(1).reset_index().sort_values('Date')
print(trend.tail(20).to_string(index=False))


# ============================================================
# PROBLEM 4: Which states approve the most vs least?
# ============================================================

print("\n--- P4: State Approval Rates ---")
state_rates = state_df.groupby('State Code')['Allowance Rate (All Initial)']\
    .mean().round(1).reset_index()
state_rates.columns = ['State Code', 'avg_allowance_rate']

print("Top 10 highest approval rates:")
print(state_rates.sort_values('avg_allowance_rate', ascending=False).head(10).to_string(index=False))

print("\nTop 10 lowest approval rates:")
print(state_rates.sort_values('avg_allowance_rate').head(10).to_string(index=False))


# ============================================================
# PROBLEM 5: SSDI vs SSI vs Concurrent approval rates
# ============================================================

print("\n--- P5: Approval Rates by Claim Type ---")
ssdi = state_df.groupby('State Code')['Allowance Rate (Initial SSDI Only)'].mean().round(1)
ssi = state_df.groupby('State Code')['Allowance Rate (Initial SSI Only)'].mean().round(1)
concurrent = state_df.groupby('State Code')['Allowance Rate (Initial Concurrent Only)'].mean().round(1)

comparison = pd.DataFrame({
    'SSDI Rate': ssdi,
    'SSI Rate': ssi,
    'Concurrent Rate': concurrent
}).reset_index()

print("National averages by claim type:")
print(comparison[['SSDI Rate', 'SSI Rate', 'Concurrent Rate']].mean().round(1))

comparison['ssdi_ssi_gap'] = round(comparison['SSDI Rate'] - comparison['SSI Rate'], 1)
print("\nTop 10 states with largest SSDI vs SSI gap:")
print(comparison[['State Code', 'SSDI Rate', 'SSI Rate', 'ssdi_ssi_gap']]\
    .sort_values('ssdi_ssi_gap', ascending=False).head(10).to_string(index=False))


# ============================================================
# DEEPER ANALYSIS R2: National backlog trend (last 3 years)
# ============================================================

print("\n--- R2: National Backlog Trend (2023-2026) ---")
national_trend = state_df.groupby('Date').agg(
    total_receipts=('Receipts (All Initial)', 'sum'),
    total_determinations=('Determinations (All Initial)', 'sum')
).reset_index()
national_trend['gap'] = national_trend['total_receipts'] - national_trend['total_determinations']

three_years = national_trend[national_trend['Date'] >= '2023-01-01'].sort_values('Date')
print(three_years[['Date', 'total_receipts', 'total_determinations', 'gap']].to_string(index=False))


# ============================================================
# DEEPER ANALYSIS R3: Which states improved vs declined (2020-2025)?
# ============================================================

print("\n--- R3: State Approval Rate Change (2020 vs 2025) ---")
early = state_df[state_df['Date'].dt.year == 2020]\
    .groupby('State Code')['Allowance Rate (All Initial)'].mean().round(1)
recent = state_df[state_df['Date'].dt.year == 2025]\
    .groupby('State Code')['Allowance Rate (All Initial)'].mean().round(1)

improvement = pd.DataFrame({'2020 Rate': early, '2025 Rate': recent}).reset_index()
improvement['change'] = round(improvement['2025 Rate'] - improvement['2020 Rate'], 1)

print("Most improved states:")
print(improvement.sort_values('change', ascending=False).head(5).to_string(index=False))
print("\nMost declined states:")
print(improvement.sort_values('change').head(5).to_string(index=False))


# ============================================================
# DEEPER ANALYSIS R4: How long to clear backlog at current pace?
# ============================================================

print("\n--- R4: Months to Clear Backlog at Current Processing Rate ---")
latest['months_to_clear'] = round(
    latest['Closing Pending (All Initial)'] /
    latest['Determinations (All Initial)'], 1
)

result = latest[['State Code', 'Closing Pending (All Initial)',
                 'Determinations (All Initial)', 'months_to_clear']]\
    .sort_values('months_to_clear', ascending=False)\
    .head(10)
print(result.to_string(index=False))


# ============================================================
# DEEPER ANALYSIS R5: Does faster processing = lower approval?
# ============================================================

print("\n--- R5: Correlation — Processing Speed vs Approval Rate ---")
corr_data = latest.copy()
corr_data['processing_rate'] = (
    corr_data['Determinations (All Initial)'] /
    corr_data['Receipts (All Initial)'] * 100
)
correlation = corr_data['processing_rate'].corr(corr_data['Allowance Rate (All Initial)'])
print(f"Correlation between processing rate and approval rate: {round(correlation, 3)}")
print("Interpretation: Negative = faster processing correlates with lower approval rates")