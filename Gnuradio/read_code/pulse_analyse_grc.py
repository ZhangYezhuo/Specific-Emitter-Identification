import struct
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from tftb.processing import WignerVilleDistribution
from PyEMD import EMD, Visualisation
import emd
import pywt

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

filepath = 'D:/GNUradio/data/20230801/device_4/device_4_cw'
# filepath = '../dataset_grc/all_mod_snr/noise/15dB'
sample_rate = 16e6  # 采样率，用于频谱绘制
seq_len_mag = 2500000
seq_len_iq = seq_len_mag * 2

# 二进制文件读取
binfile = open(filepath, 'rb')  # 打开二进制文件
size = os.path.getsize(filepath)  # 获得文件大小
data_bin = []
data_int = []
for i in range(seq_len_iq):
    data = binfile.read(4)  # float数据流为4×8bit
    if len(data)!=4:break
    num = struct.unpack('f', data)
    data_bin.append(data)
    data_int.append(num[0])
binfile.close()

# 划分IQ信号
re = np.array(data_int[0::2])
im = np.array(data_int[1::2])

# 脉冲序列预处理
# if_signal = if_signal - np.mean(if_signal)  # 去直流
# im = im - np.mean(im)
re = re / np.abs(np.max(re))  # 归一化
im = im / np.abs(np.max(im))
mag = np.sqrt(re ** 2 + im ** 2)
time = np.arange(0, len(mag)) * 1e6 / sample_rate

# 显示所有脉冲
plt.subplot(3, 1, 1)
plt.plot(time, re)
plt.title('Real Signal')
plt.ylabel('Amplitude [Voltage]')
plt.xlabel('Time [us]')
plt.tight_layout()

plt.subplot(3, 1, 2)
plt.plot(time, im)
plt.title('Imaginary Signal')
plt.ylabel('Amplitude [Voltage]')
plt.xlabel('Time [us]')
plt.tight_layout()

plt.subplot(3, 1, 3)
plt.plot(time, mag)
plt.title('Magnitude Signal')
plt.ylabel('Amplitude [Voltage]')
plt.xlabel('Time [us]')
plt.tight_layout()
plt.show(block=True)

points = 512
correlation = np.real(self_correlate(re + im * 1j))
correlation_gate = np.mean(correlation)  # 选择自相关门限
print(correlation_gate)
plt.subplot(2, 1, 1)
plt.plot(re)
plt.tight_layout()
plt.subplot(2, 1, 2)
plt.plot(correlation)
plt.tight_layout()
plt.show(block=True)

# 脉冲检测
pulse_len = int(sample_rate / 10000)  # 单个脉冲的采样序列长度
win_var = np.array([])  # 滑动窗口
for i in range(2 * pulse_len):
    win_var = np.append(win_var, np.var(re[i:i + pulse_len]))
skip_len = np.argmax(win_var)

# 划分单个脉冲
re_skip = re[skip_len::]
im_skip = im[skip_len::]
pulse_num = (seq_len_mag - skip_len) // (pulse_len * 2)  # 计算脉冲个数

print(pulse_num)

re_all_seq = np.zeros([pulse_num, pulse_len])
im_all_seq = np.zeros([pulse_num, pulse_len])

# 生成全部脉冲序列
for i in range(pulse_num):
    re_all_seq[i] = re_skip[i * pulse_len * 2:i * pulse_len * 2 + pulse_len]
    re_all_seq[i] = re_all_seq[i] / np.max(np.abs(re_all_seq[i]))
    im_all_seq[i] = im_skip[i * pulse_len * 2:i * pulse_len * 2 + pulse_len]
    im_all_seq[i] = im_all_seq[i] / np.max(np.abs(im_all_seq[i]))

# # 显示全部脉冲
# for i in range(pulse_num):
#     plt.figure(i)
#     plt.plot(if_all_seq[i])
#     plt.title('Signal')
#     plt.ylabel('Amplitude [Voltage]')
#     plt.xlabel('Time [us]')
#     plt.show(block=True)

# 指定分析对象
pulse_analyse_num = 0  # 脉冲索引
pulse_analyse_re = re_all_seq[pulse_analyse_num]
pulse_analyse_im = im_all_seq[pulse_analyse_num]
pulse_analyse_time = np.arange(0, len(pulse_analyse_re)) * 1e6 / sample_rate

# 信噪比估计
pulse_analyse_power = np.mean(pulse_analyse_re ** 2)  # 计算脉冲功率
snr = snr_m2m4_real(pulse_analyse_re)
print(snr)

# 时域
plt.plot(pulse_analyse_time, pulse_analyse_re)
plt.title('Time Domain')
plt.ylabel('Amplitude [Voltage]')
plt.xlabel('Time [us]')
plt.tight_layout()
# plt.show(block=True)

# # 频谱
# plt.subplot(3, 1, 2)
# freq = np.fft.fft(pulse_analyse_re)
# freq_abs = np.fft.fftshift(np.abs(freq))
# freq_abs = freq_abs / len(pulse_analyse_re)  # 归一化幅值
# # freq_abs = 10 * np.log10(freq_abs * 2 / np.max(freq_abs))
# # freq_axis = np.linspace(-sample_rate / 2, sample_rate / 2, len(freq_abs))
# freq_axis = np.linspace(0, sample_rate / 2, int(len(freq_abs) // 2))
# freq_abs = freq_abs[int(len(freq_abs) // 2):]
# plt.plot(freq_axis, freq_abs)
# plt.title('Frequency Domain')
# plt.ylabel('Amplitude')
# plt.xlabel('Freq [Hz]')
# plt.tight_layout()
# # plt.show(block=True)

# # 包络谱
# plt.subplot(3, 1, 3)
# pulse_analyse_hilbert = np.abs(signal.hilbert(pulse_analyse_re))
# plt.plot(pulse_analyse_time, pulse_analyse_hilbert)
# plt.title('Hilbert Spectrum')
# plt.ylabel('Amplitude [Voltage]')
# plt.xlabel('Time [us]')
# plt.tight_layout()
# plt.show(block=True)

# # 功率谱
# correlate = np.correlate(pulse_analyse_re, pulse_analyse_re, 'same')
# freq = np.fft.fft(pulse_analyse_re)
# freq_abs = np.fft.fftshift(np.abs(freq))
# freq_abs = freq_abs / len(pulse_analyse_re)  # 归一化幅值
# # freq_abs = 10 * np.log10(freq_abs * 2 / np.max(freq_abs))
# # freq_axis = np.linspace(-sample_rate / 2, sample_rate / 2, len(freq_abs))
# freq_axis = np.linspace(0, sample_rate / 2, int(len(freq_abs) // 2))
# psd = freq_abs[int(len(freq_abs) // 2):]
# plt.plot(psd)
# plt.tight_layout()
# plt.show(block=True)

# # 功率谱
# freq = np.fft.fft(pulse_analyse_re)
# freq_abs = np.fft.fftshift(np.abs(freq))
# freq_abs = freq_abs / len(pulse_analyse_re)  # 归一化幅值
# # freq_abs = 10 * np.log10(freq_abs * 2 / np.max(freq_abs))
# # freq_axis = np.linspace(-sample_rate / 2, sample_rate / 2, len(freq_abs))
# freq_axis = np.linspace(0, sample_rate / 2, int(len(freq_abs) // 2))
# freq_abs = freq_abs[int(len(freq_abs) // 2):]
# psd = freq_abs ** 2 / len(freq_abs)
# plt.plot(psd)
# plt.tight_layout()
# plt.show(block=True)

# # STFT
# plt.subplot(2, 2, 1)
# stft_nperseg = 256//2
# f, t, Zxx = signal.stft(pulse_analyse_re, sample_rate, nperseg=stft_nperseg)
# plt.pcolormesh(t * 1e6, f, np.abs(Zxx))
# plt.title('STFT Magnitude nperseg = ' + str(stft_nperseg))
# plt.ylabel('Frequency [Hz]')
# plt.xlabel('Time [us]')
# plt.ylim(0, 2e6)
# plt.tight_layout()
# # plt.axis('off')
# # plt.margins(0, 0)
# # plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
# # plt.show(block=True)

# # CWT
# plt.subplot(2, 2, 2)
# wavename = 'morl'  # morl, mexh, gaus8, cgau8
# totalscale = 1024 * 2
# wave_center_freq = pywt.central_frequency(wavelet=wavename)
# cparam = 2 * wave_center_freq * totalscale
# scales = cparam / np.arange(totalscale, 0, -1)
# [cwtmatr, frequencies] = pywt.cwt(pulse_analyse_re, scales, wavename, 1.0 / sample_rate)
# plt.pcolormesh(pulse_analyse_time, frequencies, np.abs(cwtmatr))
# plt.title('CWT ' + wavename + ' Magnitude')
# plt.ylabel('Scales [Hz]')
# plt.xlabel('Time [us]')
# plt.ylim(0, 2e6)
# plt.tight_layout()

# # CWT
# plt.subplot(2, 2, 3)
# wavename = 'gaus8'
# totalscale = 1024
# wave_center_freq = pywt.central_frequency(wavelet=wavename)
# cparam = 2 * wave_center_freq * totalscale
# scales = cparam / np.arange(totalscale, 0, -1)
# [cwtmatr, frequencies] = pywt.cwt(pulse_analyse_re, scales, wavename, 1.0 / sample_rate)
# plt.pcolormesh(pulse_analyse_time, frequencies, np.abs(cwtmatr))
# plt.title('CWT ' + wavename + ' Magnitude')
# plt.ylabel('Scales [Hz]')
# plt.xlabel('Time [us]')
# plt.ylim(0, 2e6)
# plt.tight_layout()
# # plt.show(block=True)

# # HHT谱
# plt.subplot(2, 2, 4)
# imf = emd.sift.sift(pulse_analyse_re)
# IP, IF, IA = emd.spectra.frequency_transform(imf, sample_rate, 'hilbert')
# f, hht = emd.spectra.hilberthuang(IF, IA, sum_time=False)
# picture = plt.pcolormesh(pulse_analyse_time, f, hht)
# plt.title('HHT Magnitude')
# plt.ylabel('Frequency [Hz]')
# plt.xlabel('Time [us]')
# plt.ylim(0, 2e6)
# plt.tight_layout()
# plt.show(block=True)

# # 边际谱
# marginal = np.sum(hht, 1)
# plt.plot(f, marginal)
# plt.title('Marginal spectrum')
# plt.ylabel('Amplitude [Voltage]')
# plt.xlabel('Freq [Hz]')
# plt.tight_layout()
# plt.show(block=True)

# WVD
wvd = WignerVilleDistribution(pulse_analyse_re)
tfr_wvd, t_wvd, f_wvd = wvd.run()
t_wvd = t_wvd * 1e6 / sample_rate
picture = plt.pcolormesh(t_wvd, f_wvd, np.abs(tfr_wvd))
plt.title('WVD Magnitude')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [us]')
plt.ylim(0, 0.1)
plt.show(block=True)

# # EMD
# imf = emd.sift.sift(pulse_analyse_re)
# emd.plotting.plot_imfs(imf)
# plt.show(block=True)

# # DWT
# waveletname = 'db5'  # db1为小波名称，1代表消失矩，消失矩数字越大小波越光滑
# coeffs = pywt.wavedec(pulse_analyse_re, waveletname, level=4)  # 4阶滤波
# cA4, cD4, cD3, cD2, cD1 = coeffs  # coeff小波系数
# fig, axarr = plt.subplots(nrows=len(coeffs), ncols=1)  # fig图像，axarr坐标轴
# axarr[0].plot(cD1, 'r')  # cD为细节分量(list),相当于通过高通滤波器，包含高频信息
# axarr[0].set_ylabel('cD1')
# axarr[1].plot(cD2, 'g')
# axarr[1].set_ylabel('cD2')
# axarr[2].plot(cD3, 'y')
# axarr[2].set_ylabel('cD3')
# axarr[3].plot(cD4, 'b')
# axarr[3].set_ylabel('cD4')
# axarr[4].plot(cA4, 'r')  # cA为逼近分量(list),相当于通过低通滤波器，包含低频信息
# axarr[4].set_ylabel('cA4')
# axarr[0].set_title('Coefficients')
# plt.tight_layout()
# plt.show(block=True)
