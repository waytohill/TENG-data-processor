import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
import os

# 忽略FFT中由于d=0导致的警告
warnings.filterwarnings('ignore', category=RuntimeWarning)

def compute_metrics(orig, denoised, max_val=None):
    mse = np.mean((orig - denoised) ** 2)
    signal_power = np.sum(orig ** 2)
    noise_power = np.sum((orig - denoised) ** 2)
    snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else np.inf
    if max_val is None:
        max_val = np.max(np.abs(orig))
    psnr = 10 * np.log10(max_val ** 2 / mse) if mse > 0 else np.inf
    corr = np.corrcoef(orig, denoised)[0, 1] if mse > 0 else np.nan
    return {'MSE': mse, 'SNR(dB)': snr, 'PSNR(dB)': psnr, 'CorrCoeff': corr}

def plot_time_domain(time, orig, den1, den2):
    plt.figure()
    ax = plt.gca()
    if np.issubdtype(time.dtype, np.datetime64):
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.plot(time, orig, label='Original')
    plt.plot(time, den1, label='Denoised 1')
    plt.plot(time, den2, label='Denoised 2')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.title('Time-domain Signal Comparison')
    plt.legend()
    if np.issubdtype(time.dtype, np.datetime64):
        plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.show()

def plot_frequency_domain(orig, den1, den2, fs=None):
    n = len(orig)
    # 确保采样频率有效
    if fs is None or fs <= 0:
        # 默认单位采样间隔
        freq = np.fft.rfftfreq(n, d=1.0)
    else:
        freq = np.fft.rfftfreq(n, d=1.0/fs)
    orig_fft = np.abs(np.fft.rfft(orig))
    den1_fft = np.abs(np.fft.rfft(den1))
    den2_fft = np.abs(np.fft.rfft(den2))
    plt.figure()
    plt.plot(freq, orig_fft, label='Original')
    plt.plot(freq, den1_fft, label='Denoised 1')
    plt.plot(freq, den2_fft, label='Denoised 2')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.title('Frequency-domain Signal Comparison')
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title='Select CSV File',
        filetypes=[('CSV Files', '*.csv'), ('All Files', '*.*')]
    )
    if not file_path:
        print('No file selected. Exiting.')
        return

    df = pd.read_csv(file_path)
    time_raw = df.iloc[:, 0]
    try:
        time = pd.to_datetime(time_raw)
    except Exception:
        time = time_raw.values.astype(float)

    orig = df.iloc[:, 1].to_numpy()
    den1 = df.iloc[:, 2].to_numpy()
    den2 = df.iloc[:, 3].to_numpy()

    # 估计采样频率
    fs = None
    if np.issubdtype(type(time[0]), np.datetime64) and len(time) > 1:
        dt = np.diff(time.astype('int64')) / 1e9
        # 仅当时间间隔一致且大于0时才设定fs
        if np.allclose(dt, dt[0]) and dt[0] > 0:
            fs = 1.0 / dt[0]

    metrics1 = compute_metrics(orig, den1)
    metrics2 = compute_metrics(orig, den2)

    print("Metrics for Denoised 1 vs Original:")
    for k, v in metrics1.items():
        print(f"  {k}: {v:.4f}")
    print("\nMetrics for Denoised 2 vs Original:")
    for k, v in metrics2.items():
        print(f"  {k}: {v:.4f}")

    plot_time_domain(time, orig, den1, den2)
    plot_frequency_domain(orig, den1, den2, fs)

    result_df = pd.DataFrame([metrics1, metrics2], index=['Denoised1', 'Denoised2'])
    save_path = os.path.join(os.path.dirname(file_path), 'denoise_metrics.csv')
    result_df.to_csv(save_path)
    print(f"Metrics saved to {save_path}")

if __name__ == '__main__':
    main()
