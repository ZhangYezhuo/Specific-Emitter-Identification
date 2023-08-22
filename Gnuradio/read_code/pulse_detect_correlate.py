import struct
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import emd
import pywt
from tftb.processing import WignerVilleDistribution
from utils import filter_bp, deal_hist, snr_m2m4_real, self_correlate
from tqdm import tqdm

device="device_5"
mode="qfsk_bpsk"
filepath = 'D:/GNUradio/data/20230801/{0}/{1}_{2}'.format(device, device, mode)
sample_rate = 16e6  # 采样率，用于频谱绘制

# 二进制文件读取
binfile = open(filepath, 'rb')  # 打开二进制文件
size = os.path.getsize(filepath)  # 获得文件大小
data_bin = []
data_int = []

print("Unpacking data of size {}, please wait...".format(size))
for i in range(int(size/8*2)):# 8bit 2route
    data = binfile.read(4)  # float数据流为4×8bit
    num = struct.unpack('f', data)
    data_bin.append(data)
    data_int.append(num[0])
binfile.close()

# 划分IQ信号
re = np.array(data_int[0::2])
im = np.array(data_int[1::2])
re = re / np.abs(np.max(re))  # 归一化
im = im / np.abs(np.max(im))
mag = np.sqrt(re ** 2 + im ** 2)

# 脉冲预处理
points = 16  # 自相关点数
correlation = np.real(self_correlate(seq=re + im * 1j, points=points))
correlation_gate = (np.max(correlation) + np.min(correlation)) / 16  # 选择自相关门限
print("gate: {}".format(correlation_gate))

# 脉冲检测
len_thr=100
pulse_index = np.array([])
pulse_index_all = []
for i in tqdm(range(len(correlation))):
    if correlation[i] >= correlation_gate:
        pulse_index = np.append(pulse_index, i + int(points//2))  # 起始位置修正
    else:
        if len(pulse_index) >= points:
            pulse_index = pulse_index.astype(int)  # int型才可以用于索引
            if len(pulse_index)>len_thr:
                pulse_index_all.append(pulse_index)
            pulse_index = np.array([])
        else:
            pulse_index = np.array([])

# output module
print("pulse number: {}".format(len(pulse_index_all)))
if not os.path.exists('D:/GNUradio/data/20230801/{0}_{1}/'.format(device, mode)):
    os.mkdir('D:/GNUradio/data/20230801/{0}_{1}/'.format(device, mode))
for i in tqdm(range(len(pulse_index_all))):
    np.save('D:/GNUradio/data/20230801/{0}_{1}/{2}_{3}_{4}.npy'.format(device, mode, str(i).rjust(4, "0"), device, mode), 
            np.append(re[pulse_index_all[i]], im[pulse_index_all[i]]))

# plt.plot(re[pulse_index_all[0]])
# plt.show()

# stft_nperseg = 256//4
# f, t, Zxx = signal.stft(pulse_signal[pulse_index_all[0]], sample_rate, nperseg=stft_nperseg)
# plt.pcolormesh(t * 1e6, f, np.abs(Zxx))
# plt.title('STFT Magnitude nperseg = ' + str(stft_nperseg))
# plt.ylabel('Frequency [Hz]')
# plt.xlabel('Time [us]')
# plt.ylim(0, 2e6)
# plt.show(block=True)


# wvd = WignerVilleDistribution(pulse_signal[pulse_index_all[0]])
# tfr_wvd, t_wvd, f_wvd = wvd.run()
# t_wvd = t_wvd * 1e6 / sample_rate
# picture = plt.pcolormesh(t_wvd, f_wvd, np.abs(tfr_wvd))
# plt.title('WVD Magnitude')
# plt.ylabel('Frequency [Hz]')
# plt.xlabel('Time [us]')
# # plt.ylim(0, 0.1)
# plt.show(block=True)
