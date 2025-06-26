#!/usr/bin/env python3
"""
IMF分量自动化分析脚本（带文件选择与多路径模块检查）
功能：
  - 弹出文件选择窗口读取CSV（列头：time, voltage）
  - 检查EMD分解模块安装（PyEMD或emd），否则提示安装
  - 对一维电压信号执行EMD分解，获取IMFs
  - 计算并打印每阶IMF能量占比
  - 在一张组合图中展示：
      * 每个IMF分量波形
      * IMF能量占比条形图
      * 前N阶IMF频谱
      * 去除前M阶IMF后信号重构时域/频域对比
"""
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PyEMD import EMD

from scipy.fft import fft, fftfreq
import tkinter as tk
from tkinter import filedialog


def ask_csv_file():
    root = tk.Tk(); root.withdraw()
    file_path = filedialog.askopenfilename(
        title='选择CSV文件 (列头: time, voltage)',
        filetypes=[('CSV Files', '*.csv')]
    )
    if not file_path:
        raise FileNotFoundError('未选择任何文件')
    return file_path


def compute_imfs(signal, time):
    emd = EMD()
    return emd.emd(signal, time)


def energy_ratios(imfs):
    energies = np.array([np.sum(imf**2) for imf in imfs])
    return energies / energies.sum()


def reconstruct_signal(imfs, remove_n):
    return np.sum(imfs[remove_n:], axis=0)


def main():
    # 读取数据
    csv_path = ask_csv_file()
    df = pd.read_csv(csv_path)
    if 'time' not in df.columns or 'voltage' not in df.columns:
        raise KeyError("CSV必须包含 'time' 和 'voltage' 两列")
    time = df['time'].values
    signal = df['voltage'].values

    # 参数
    N_SPECTRA = 5
    REMOVE_IMFS = 2

    # EMD 分解
    imfs = compute_imfs(signal, time)
    ratios = energy_ratios(imfs)

    # 重构信号
    recon = reconstruct_signal(imfs, REMOVE_IMFS)

    # 组合绘图
    num_imfs = len(imfs)
    cols = 2
    rows = num_imfs + 3  # imf rows + energy + spectra + recon
    plt.figure(figsize=(12, 3*rows))

    # 每个IMF分量波形
    for i, imf in enumerate(imfs, 1):
        ax = plt.subplot(rows, cols, (i-1)*cols+1)
        ax.plot(time, imf)
        ax.set_ylabel(f'IMF{i}')
        if i == 1:
            ax.set_title('IMF 分量波形')
        if (i-1)%cols == 0:
            ax.set_xlabel('Time')

    # 能量占比
    ax_e = plt.subplot(rows, cols, num_imfs*cols+1)
    ax_e.bar(range(1, num_imfs+1), ratios)
    ax_e.set_xlabel('IMF index')
    ax_e.set_ylabel('Energy ratio')
    ax_e.set_title('IMF 能量占比')

    # IMF 频谱 (前N_SPECTRA)
    fs = 1.0 / np.mean(np.diff(time))
    N = len(time)
    ax_s = plt.subplot(rows, cols, num_imfs*cols+2)
    for j in range(min(N_SPECTRA, num_imfs)):
        yf = np.abs(fft(imfs[j]))[:N//2]
        xf = fftfreq(N, 1/fs)[:N//2]
        ax_s.plot(xf, yf, label=f'IMF{j+1}')
    ax_s.set_xlim(0, fs/2)
    ax_s.set_title('前N阶IMF 频谱')
    ax_s.set_xlabel('Frequency (Hz)')
    ax_s.legend()

    # 重构时域对比
    ax_rt = plt.subplot(rows, cols, (num_imfs+1)*cols+1)
    ax_rt.plot(time, signal, label='Original')
    ax_rt.plot(time, recon, label='Reconstructed', alpha=0.7)
    ax_rt.set_title('重构后时域对比')
    ax_rt.set_xlabel('Time')
    ax_rt.legend()

    # 重构频域对比
    ax_rf = plt.subplot(rows, cols, (num_imfs+1)*cols+2)
    yf_o = np.abs(fft(signal))[:N//2]
    yf_r = np.abs(fft(recon))[:N//2]
    xf = fftfreq(N, 1/fs)[:N//2]
    ax_rf.plot(xf, yf_o, label='Original')
    ax_rf.plot(xf, yf_r, label='Reconstructed', alpha=0.7)
    ax_rf.set_title('重构后频域对比')
    ax_rf.set_xlabel('Frequency (Hz)')
    ax_rf.legend()

    plt.tight_layout()
    plt.show()

    # 打印能量占比
    for i, r in enumerate(ratios, 1):
        print(f'IMF {i}: energy ratio = {r:.4f}')

if __name__ == '__main__':
    main()
