import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pywt
import warnings
import os

warnings.filterwarnings('ignore', category=RuntimeWarning)

# -- CWT Analysis Functions --
def compute_cwt(data, scales, wavelet='gaus1', dt=1.0):
    """
    Compute CWT coefficients using sampling period dt.
    Returns coefficients, power, and frequencies.
    """
    coeffs, freqs = pywt.cwt(data, scales, wavelet, sampling_period=dt)
    power = np.abs(coeffs) ** 2
    return coeffs, power, freqs


def compute_global_spectrum(power):
    """
    Compute Global Wavelet Spectrum (time-averaged power over scales).
    """
    return np.mean(power, axis=1)


def extract_wavelet_ridge(power, freqs):
    """
    Extract wavelet ridge frequencies (instantaneous dominant frequency).
    """
    ridge_idx = np.argmax(power, axis=0)
    return freqs[ridge_idx]

# -- Plotting Functions --
def plot_scalogram(time, power, freqs, title='Scalogram'):
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    extent = [time[0], time[-1], freqs[-1], freqs[0]]
    im = ax.imshow(power, extent=extent, aspect='auto', cmap='jet')
    ax.set_xlabel('Time (s)')
    ax.set_xlim(time[0], time[-1])
    ax.set_ylabel('Frequency (Hz)')
    ax.set_title(title)
    plt.colorbar(im, label='Power')
    plt.tight_layout()


def plot_global_spectrum(freqs, gws_orig, gws_denoised):
    plt.figure()
    plt.plot(freqs, gws_orig, label='Original GWS')
    plt.plot(freqs, gws_denoised, label='Denoised GWS')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Mean Power')
    plt.title('Global Wavelet Spectrum Comparison')
    plt.legend()
    plt.tight_layout()


def plot_ridge(time, ridge_orig, ridge_denoised):
    plt.figure()
    plt.plot(time, ridge_orig, label='Original Ridge Freq')
    plt.plot(time, ridge_denoised, label='Denoised Ridge Freq')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title('Wavelet Ridge Comparison')
    plt.legend()
    plt.tight_layout()

# -- Main --
def main():
    # File selection dialog
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(title='Select CSV File', filetypes=[('CSV', '*.csv')])
    if not path:
        print('No file selected. Exiting.')
        return

    # Read data
    df = pd.read_csv(path)
    orig = df.iloc[:, 1].to_numpy()
    den = df.iloc[:, 2].to_numpy()

    # Sampling rate and period
    fs = 500.0  # Hz
    dt = 1.0 / fs

    # Generate time vector
    n = len(orig)
    time = np.arange(n) * dt

    # Define CWT scales
    max_scale = min(n // 2, 128)
    scales = np.linspace(1, max_scale, num=100)

    # Compute CWT and power
    coeff_o, power_o, freqs = compute_cwt(orig, scales, dt=dt)
    coeff_d, power_d, _ = compute_cwt(den, scales, dt=dt)

    # Extract features
    gws_o = compute_global_spectrum(power_o)
    gws_d = compute_global_spectrum(power_d)
    ridge_o = extract_wavelet_ridge(power_o, freqs)
    ridge_d = extract_wavelet_ridge(power_d, freqs)

    # Plot analyses
    plot_scalogram(time, power_o, freqs, title='Original Signal Scalogram')
    plot_scalogram(time, power_d, freqs, title='Denoised Signal Scalogram')
    plot_global_spectrum(freqs, gws_o, gws_d)
    plot_ridge(time, ridge_o, ridge_d)

    # Prepare and save all computed data
    # Time-series results
    result_df = pd.DataFrame({
        'Time(s)': time,
        'Original': orig,
        'Denoised': den,
        'Ridge_Orig(Hz)': ridge_o,
        'Ridge_Denoised(Hz)': ridge_d
    })
    # Global Wavelet Spectrum
    gws_df = pd.DataFrame({
        'Frequency(Hz)': freqs,
        'GWS_Orig': gws_o,
        'GWS_Denoised': gws_d
    })
    # Scalogram data as DataFrame (scales x time)
    scalogram_o_df = pd.DataFrame(power_o, index=scales, columns=time)
    scalogram_d_df = pd.DataFrame(power_d, index=scales, columns=time)

    # Create output file paths
    base, _ = os.path.splitext(path)
    result_path = f"{base}_cwt_timeseries.csv"
    gws_path = f"{base}_cwt_gws.csv"
    scalo_o_path = f"{base}_scalogram_orig.csv"
    scalo_d_path = f"{base}_scalogram_denoised.csv"

    result_df.to_csv(result_path, index=False)
    gws_df.to_csv(gws_path, index=False)
    scalogram_o_df.to_csv(scalo_o_path)
    scalogram_d_df.to_csv(scalo_d_path)

    print(f"Saved timeseries results to: {result_path}")
    print(f"Saved global spectrum to: {gws_path}")
    print(f"Saved original scalogram to: {scalo_o_path}")
    print(f"Saved denoised scalogram to: {scalo_d_path}")

    plt.show()

if __name__ == '__main__':
    main()
