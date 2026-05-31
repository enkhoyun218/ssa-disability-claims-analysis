from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

master = pd.read_csv("/Users/enkh-oyun0218/Documents/data-projects/master_dataset.csv")

hypotheses = [
    ('H1', 'poverty_rate', 'avg_allowance_rate', 'Poverty Rate (%)', 'Avg Approval Rate (%)'),
    ('H2', 'physicians_per_100k', 'avg_allowance_rate', 'Physicians per 100k', 'Avg Approval Rate (%)'),
    ('H3', 'demanding_industry_pct', 'avg_receipts', 'Demanding Industry %', 'Avg Receipts'),
    ('H5', 'processing_rate', 'avg_allowance_rate', 'Processing Rate (%)', 'Avg Approval Rate (%)'),
    ('H5b', 'unemployment_rate', 'avg_allowance_rate', 'Unemployment Rate (%)', 'Avg Approval Rate (%)'),
    ('H6', 'demanding_industry_pct', 'avg_allowance_rate', 'Demanding Industry %', 'Avg Approval Rate (%)'),
]

for h_name, var1, var2, xlabel, ylabel in hypotheses:
    x = master[var1]
    y = master[var2]

    # 1. Correlation + p-value
    corr, p_value = stats.pearsonr(x, y)

    # 2. Effect size
    r_squared = corr ** 2

    # 3. Interpretation
    if abs(corr) >= 0.5:
        strength = "strong"
    elif abs(corr) >= 0.3:
        strength = "moderate"
    else:
        strength = "weak"

    print(f"\n{h_name}: {var1} vs {var2}")
    print(f"  Correlation: {round(corr, 3)}")
    print(f"  P-value: {round(p_value, 4)} → {'Significant' if p_value < 0.05 else 'Not significant'}")
    print(f"  R-squared: {round(r_squared*100, 1)}% of variance explained")
    print(f"  Strength: {strength}")

    # 4. Visualization
    plt.figure(figsize=(8, 5))
    plt.scatter(x, y, alpha=0.6, color='steelblue')

    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m*x + b, color='red', linewidth=2)

    for i, row in master.iterrows():
        plt.annotate(row['State Code'],
                    (row[var1], row[var2]),
                    fontsize=7, alpha=0.7)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f'{h_name}: {xlabel} vs {ylabel} (r={round(corr,3)}, p={round(p_value,4)})')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{h_name}_scatter.png')
    plt.close()

# H4 - Political Party (separate since it uses groupby)
print("\nH4: Political Party vs Approval Rate")
party_avg = master.groupby('political_party')['avg_allowance_rate'].mean().round(1)
print(f"  Republican states: {party_avg.get('R', 'N/A')}%")
print(f"  Democrat states:   {party_avg.get('D', 'N/A')}%")
print(f"  Difference: {round(abs(party_avg.get('R', 0) - party_avg.get('D', 0)), 1)} points")