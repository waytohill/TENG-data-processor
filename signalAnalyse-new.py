import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load and preprocess data
df = pd.read_csv('curve1.csv')
df_clean = df.dropna(subset=['signal1', 'signal2'])
time = df_clean['time'].values
sig1 = df_clean['signal1'].values
sig2 = df_clean['signal2'].values

# Save cleaned data
cleaned_path = 'curve1_processed.csv'
df_clean.to_csv(cleaned_path, index=False)

# Overall metrics
mse = np.mean((sig1 - sig2)**2)
pearson_r = np.corrcoef(sig1, sig2)[0, 1]

# DTW implementation
def dtw_distance(a, b):
    n, m = len(a), len(b)
    dtw = np.full((n+1, m+1), np.inf)
    dtw[0, 0] = 0
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = abs(a[i-1] - b[j-1])
            dtw[i, j] = cost + min(dtw[i-1, j], dtw[i, j-1], dtw[i-1, j-1])
    return dtw[n, m]

dtw_dist = dtw_distance(sig1, sig2)

# Cross-correlation
corr_full = np.correlate(sig1 - sig1.mean(), sig2 - sig2.mean(), mode='full')
lag = corr_full.argmax() - (len(sig1) - 1)
dt = time[1] - time[0] if len(time) > 1 else 0
max_corr = corr_full.max() / (np.std(sig1) * np.std(sig2) * len(sig1))

# Sliding window metrics
window_size = 50
step = 10
centers, mse_windows, r_windows = [], [], []

for start in range(0, len(sig1) - window_size + 1, step):
    end = start + window_size
    win1, win2 = sig1[start:end], sig2[start:end]
    centers.append(time[start + window_size // 2])
    mse_windows.append(np.mean((win1 - win2)**2))
    r_windows.append(np.corrcoef(win1, win2)[0, 1])

# Prepare overall metrics DataFrame
overall_metrics = {
    'overall_mse': mse,
    'overall_pearson_r': pearson_r,
    'dtw_distance': dtw_dist,
    'max_cross_correlation': max_corr,
    'lag_samples': lag,
    'lag_seconds': lag * dt
}
df_overall = pd.DataFrame([overall_metrics])
overall_path = 'curve1_overall_metrics.csv'
df_overall.to_csv(overall_path, index=False)

# Prepare sliding window metrics DataFrame
df_sliding = pd.DataFrame({
    'time_center': centers,
    'window_mse': mse_windows,
    'window_pearson_r': r_windows
})
# Optionally include overall metrics as constant columns
for key, value in overall_metrics.items():
    df_sliding[key] = value

sliding_path = 'curve1_sliding_metrics.csv'
df_sliding.to_csv(sliding_path, index=False)

# Report
print(f'Cleaned data saved to: {cleaned_path}')
print(f'Overall metrics saved to: {overall_path}')
print(f'Sliding-window metrics saved to: {sliding_path}')

# (Plots and prints can remain unchanged)
