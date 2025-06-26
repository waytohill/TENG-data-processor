import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pywt
import scipy.stats as st
import warnings
import os

warnings.filterwarnings('ignore', category=RuntimeWarning)

# -- CWT Analysis Functions --
def compute_cwt(data, scales, wavelet='gaus1', dt=1.0):
    """
    Compute CWT coefficients using PyWavelets cwt.
    Returns coeffs (scales×time), power, and pseudo-frequencies.
    """
    coeffs, freqs = pywt.cwt(data, scales, wavelet, sampling_period=dt)
    power = np.abs(coeffs) ** 2
    return coeffs, power, freqs

def compute_global_spectrum(power):
    """Time-average over columns to get Global Wavelet Spectrum (per scale)."""
    return power.mean(axis=1)

def compute_gws_confidence(power, alpha=0.05):
    """
    Compute pointwise 100*(1-alpha)% confidence intervals for the mean power.
    Assumes approximate independence across time.
    """
    N = power.shape[1]
    mean = power.mean(axis=1)
    sem  = power.std(axis=1, ddof=1) / np.sqrt(N)
    h    = sem * st.t.ppf(1 - alpha/2, df=N-1)
    return mean - h, mean + h

def extract_wavelet_ridge(power, freqs):
    """For each time point, pick the frequency with maximum power."""
    ridge_idx = np.argmax(power, axis=0)
    return freqs[ridge_idx]

def ridge_stats(ridge_orig, ridge_den):
    """
    Compute standard deviation of each ridge and their mean relative error.
    Returns (std_orig, std_den, mean_rel_error[%]).
    """
    std_o = np.std(ridge_orig, ddof=1)
    std_d = np.std(ridge_den, ddof=1)
    rel_err = np.mean(np.abs(ridge_den - ridge_orig) / (ridge_orig + 1e-8)) * 100
    return std_o, std_d, rel_err

# -- Plotting Functions --
def plot_scalogram(time, power, freqs, title='Scalogram'):
    plt.figure(figsize=(10, 6))
    extent = [time[0], time[-1], freqs[-1], freqs[0]]
    plt.imshow(power, extent=extent, aspect='auto', cmap='jet')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title(title)
    plt.colorbar(label='Power')
    plt.tight_layout()

def plot_gws_with_conf(freqs, gws_o, gws_d, low_o, high_o, low_d, high_d):
    plt.figure(figsize=(8, 4))
    # Original GWS + CI
    plt.plot(freqs, gws_o, label='Original GWS', lw=1.5)
    plt.fill_between(freqs, low_o, high_o, color='blue', alpha=0.3)
    # Denoised GWS + CI
    plt.plot(freqs, gws_d, label='Denoised GWS', lw=1.5)
    plt.fill_between(freqs, low_d, high_d, color='orange', alpha=0.3)
    # Mark peaks
    p_o, v_o = freqs[np.argmax(gws_o)], gws_o.max()
    p_d, v_d = freqs[np.argmax(gws_d)], gws_d.max()
    plt.scatter([p_o], [v_o], color='blue')
    plt.text(p_o, v_o, f' {p_o:.2f} Hz', va='bottom')
    plt.scatter([p_d], [v_d], color='orange')
    plt.text(p_d, v_d, f' {p_d:.2f} Hz', va='bottom')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Mean Power')
    plt.title('Global Wavelet Spectrum with 95% CI')
    plt.legend()
    plt.tight_layout()

def plot_ridge(time, ridge_o, ridge_d):
    plt.figure(figsize=(8, 3))
    plt.plot(time, ridge_o, label='Original Ridge')
    plt.plot(time, ridge_d, label='Denoised Ridge')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title('Wavelet Ridge Comparison')
    plt.legend()
    plt.tight_layout()

# -- Main Script --
def main():
    # 1) Select CSV
    root = tk.Tk(); root.withdraw()
    path = filedialog.askopenfilename(
        title='Select CSV File',
        filetypes=[('CSV files','*.csv')]
    )
    if not path:
        print("No file selected. Exiting.")
        return

    # 2) Read data
    df = pd.read_csv(path)
    time = df['time'].to_numpy()
    orig = df['morphology_filt'].to_numpy()
    den  = df['denoised_data2'].to_numpy()

    # 3) Sampling period from time column
    dt = np.median(np.diff(time))
    fs = 1.0 / dt

    # 4) Define scales to focus 0.1–10 Hz
    f_min, f_max = 0.1, 10.0
    N_scales     = 150
    freqs_tgt    = np.linspace(f_max, f_min, N_scales)
    scales       = fs / freqs_tgt

    # 5) Compute CWT & power
    _, power_o, freqs = compute_cwt(orig, scales, wavelet='gaus1', dt=dt)
    _, power_d, _     = compute_cwt(den,  scales, wavelet='gaus1', dt=dt)

    # 6) GWS and confidence intervals
    gws_o     = compute_global_spectrum(power_o)
    gws_d     = compute_global_spectrum(power_d)
    low_o, high_o = compute_gws_confidence(power_o)
    low_d, high_d = compute_gws_confidence(power_d)

    # 7) Ridge extraction & stats
    ridge_o = extract_wavelet_ridge(power_o, freqs)
    ridge_d = extract_wavelet_ridge(power_d, freqs)
    std_o, std_d, rel_err = ridge_stats(ridge_o, ridge_d)

    # 8) Plot everything
    plot_scalogram(time, power_o, freqs,   'Original Signal Scalogram')
    plot_scalogram(time, power_d, freqs,   'Denoised Signal Scalogram')
    plot_gws_with_conf(freqs, gws_o, gws_d, low_o, high_o, low_d, high_d)
    plot_ridge(time, ridge_o, ridge_d)
    plt.show()

    # 9) Console output of metrics
    print(f"Original Ridge Std Dev: {std_o:.3f} Hz")
    print(f"Denoised Ridge Std Dev: {std_d:.3f} Hz")
    print(f"Mean Relative Ridge Error: {rel_err:.2f} %")
    print(f"Original GWS Peak: {freqs[np.argmax(gws_o)]:.2f} Hz @ {gws_o.max():.3e}")
    print(f"Denoised GWS Peak: {freqs[np.argmax(gws_d)]:.2f} Hz @ {gws_d.max():.3e}")

    # 10) Save results to CSV
    base, _ = os.path.splitext(path)

    # Ridge & time series
    pd.DataFrame({
        'time': time,
        'orig': orig,
        'denoised': den,
        'ridge_orig_Hz': ridge_o,
        'ridge_den_Hz': ridge_d
    }).to_csv(f'{base}_cwt_timeseries.csv', index=False)

    # Metrics summary
    pd.DataFrame([{
        'std_ridge_orig_Hz': std_o,
        'std_ridge_den_Hz':  std_d,
        'mean_rel_ridge_err_%': rel_err,
        'peak_freq_orig_Hz': freqs[np.argmax(gws_o)],
        'peak_freq_den_Hz':  freqs[np.argmax(gws_d)],
        'peak_val_orig':     gws_o.max(),
        'peak_val_den':      gws_d.max()
    }]).to_csv(f'{base}_cwt_metrics.csv', index=False)

    # GWS + CI
    pd.DataFrame({
        'freq_Hz':        freqs,
        'gws_orig':       gws_o,
        'ci_low_orig':    low_o,
        'ci_high_orig':   high_o,
        'gws_denoised':   gws_d,
        'ci_low_denoised':low_d,
        'ci_high_denoised':high_d
    }).to_csv(f'{base}_cwt_gws.csv', index=False)

    # Scalogram matrices
    pd.DataFrame(power_o, index=freqs, columns=time).to_csv(f'{base}_scalogram_orig.csv')
    pd.DataFrame(power_d, index=freqs, columns=time).to_csv(f'{base}_scalogram_den.csv')

    print("All analysis results saved.")

if __name__ == '__main__':
    main()
