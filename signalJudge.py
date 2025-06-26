#!/usr/bin/env python3
"""
TENG信号分析与评估脚本
输入：CSV文件（第一列时间、第二列电压）
输出：频率估计、时域/频域特征、运动类型分类结果及可视化展示
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks
from scipy.fft import fft, fftfreq
import argparse
import json

def bandpass_filter(signal, fs, lowcut=0.1, highcut=20.0, order=4):
    """
    对信号进行带通滤波，过滤0.1~20Hz的频率成分
    """
    # 使用 b, a 形式以兼容 filtfilt
    b, a = butter(order, [lowcut, highcut], btype='band', fs=fs)
    return filtfilt(b, a, signal)


def estimate_frequency_time(signal, fs):
    peaks, _ = find_peaks(signal, distance=fs*0.3, prominence=np.std(signal))
    if len(peaks) < 2:
        return None, peaks
    times = peaks / fs
    period = np.mean(np.diff(times))
    return 1.0 / period, peaks


def estimate_frequency_fft(signal, fs):
    N = len(signal)
    yf = fft(signal)
    xf = fftfreq(N, 1/fs)
    idx = np.argmax(np.abs(yf[:N//2]))
    return abs(xf[idx]), xf, np.abs(yf)


def extract_features(signal, fs):
    feats = {}
    feats['mean'] = np.mean(signal)
    feats['std'] = np.std(signal)
    feats['pk2pk'] = np.ptp(signal)
    spec = np.abs(fft(signal))
    xf = fftfreq(len(signal), 1/fs)
    pos = xf > 0
    feats['spectral_centroid'] = np.sum(xf[pos] * spec[pos]) / np.sum(spec[pos])
    feats['max_freq'] = xf[np.argmax(spec[:len(signal)//2])]
    feats['max_power'] = np.max(spec[:len(signal)//2])
    return feats


def classify_activity(freq, threshold=2.5):
    if freq is None:
        return 'Unknown'
    return 'Running' if freq > threshold else 'Walking'


def visualize(time, raw, filtered, fs, peaks, xf, yf):
    plt.figure(figsize=(12, 8))
    plt.subplot(3,1,1)
    plt.plot(time, raw)
    plt.title('原始电压信号')
    plt.ylabel('Voltage')

    plt.subplot(3,1,2)
    plt.plot(time, filtered)
    plt.plot(time[peaks], filtered[peaks], 'rx')
    plt.title('带通滤波后信号与峰值检测')
    plt.ylabel('Voltage')

    plt.subplot(3,1,3)
    mask = xf > 0
    plt.plot(xf[mask], yf[mask])
    plt.title('频谱分析')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')

    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description='TENG信号分析与评估（CSV）')
    parser.add_argument('--input', type=str, required=True, help='CSV文件路径')
    parser.add_argument('--threshold', type=float, default=2.5, help='频率分类阈值(Hz)')
    args = parser.parse_args()

    # 读取CSV并转换为数值型
    try:
        df = pd.read_csv(args.input, header=None)
        time = pd.to_numeric(df.iloc[:, 0], errors='coerce').values
        signal = pd.to_numeric(df.iloc[:, 1], errors='coerce').values
    except Exception as e:
        print(f"读取CSV失败：{e}")
        return

    # 检查是否有NaN值
    if np.isnan(time).any() or np.isnan(signal).any():
        print("时间或电压列存在非数值数据，请检查CSV格式。")
        return

    # 估算采样率
    dt = np.diff(time)
    if np.any(dt <= 0):
        print("时间列不严格递增，请检查CSV中的时间数据。")
        return
    fs = 1.0 / np.mean(dt)

    # 信号处理流程
    filtered = bandpass_filter(signal, fs)
    f_time, peaks = estimate_frequency_time(filtered, fs)
    f_fft, xf, yf = estimate_frequency_fft(filtered, fs)
    feats = extract_features(filtered, fs)
    activity = classify_activity(f_time if f_time is not None else f_fft, args.threshold)

    # 可视化展示
    visualize(time, signal, filtered, fs, peaks, xf, yf)

    # 输出JSON结果
    result = {
        'sampling_rate': fs,
        'freq_time_domain': f_time,
        'freq_fft': f_fft,
        'features': feats,
        'activity': activity
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
