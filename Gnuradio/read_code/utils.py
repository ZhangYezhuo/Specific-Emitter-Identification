import struct
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from tftb.processing import WignerVilleDistribution

def filter_bp(sig, sample_rate, freq_start, freq_stop, order=3):
    wn1 = 2 * freq_start / sample_rate
    wn2 = 2 * freq_stop / sample_rate
    b, a = signal.butter(order, [wn1, wn2], 'bandpass')
    sig_filter = signal.filtfilt(b, a, sig)
    return sig_filter


# 自适应阈值
def deal_hist(seq, hist_win=0.05):
    count_array = []
    label_array = []
    for idx in range(int(np.max(seq) / hist_win) + 1):
        count_array.append(0)
        label_array.append(hist_win * idx)
    for idx in range(len(seq)):
        count_array[int(seq[idx] / hist_win)] += 1
    # 找出最左边的峰值
    argmax = 0
    for idx in range(len(count_array)):
        if idx == 0 and count_array[idx] > count_array[idx + 1]:
            argmax = idx
            break
        elif 0 < idx < len(count_array) - 1 and count_array[idx] > count_array[idx + 1] and \
                count_array[idx] > count_array[idx - 1]:
            argmax = idx
            break

    return label_array[argmax + 1] + hist_win / 2


# m2m4信噪比估计算法，仅适用于实信号
def snr_m2m4_real(seq):
    m2 = np.mean(abs(seq) ** 2)
    m4 = np.mean(abs(seq) ** 4)
    ka = 1.5
    kw = 3
    power_signal = (m2 * (kw - 3) - np.sqrt((9 - ka * kw) * m2 ** 2 + m4 * (ka + kw - 6))) / (ka + kw - 6)
    power_noise = m2 - power_signal
    snr_m2m4 = 10 * np.log10(power_signal / power_noise)
    return snr_m2m4


# 自相关脉冲检测算法，针对低信噪比信号
def self_correlate(seq, points=512):  # 输入seq为复信号，points为自相关点数，可取8/64/512
    relation = []
    relation_0 = 0
    relation_1 = 0

    for index in range(points):
        relation_0 += seq[index + 1] * seq[index].conjugate()
    relation.append(relation_0)

    for index in range(1, len(seq) - points):
        relation_1 = relation_0 + seq[index + points] * seq[index - 1 + points].conjugate() - \
                     seq[index] * seq[index - 1].conjugate()
        relation.append(relation_1)
        relation_0 = relation_1

    relation = np.array(relation) / points
    return relation