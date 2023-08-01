#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: mod_pulse_nlfm
# Author: zhouzinan
# GNU Radio version: 3.10.6.0

from packaging.version import Version as StrictVersion
from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
from gnuradio import blocks
from gnuradio import channels
from gnuradio.filter import firdes
from gnuradio import filter
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
import numpy as np
import osmosdr
import sip



class mod_pulse_nlfm(gr.top_block, Qt.QWidget):

    def __init__(self, device_0="232057", device_1="8243c3", device_2="90a7c7", device_3="4a0a4f", device_4="24644f", device_5="6f2e4f", device_6="53454f"):
        gr.top_block.__init__(self, "mod_pulse_nlfm", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("mod_pulse_nlfm")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "mod_pulse_nlfm")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Parameters
        ##################################################
        self.device_0 = device_0
        self.device_1 = device_1
        self.device_2 = device_2
        self.device_3 = device_3
        self.device_4 = device_4
        self.device_5 = device_5
        self.device_6 = device_6

        ##################################################
        # Variables
        ##################################################
        self.sps = sps = 2
        self.signal_power = signal_power = 0.5
        self.pw = pw = 12.7e-6
        self.SNR = SNR = 15
        self.step_freq = step_freq = 0.2e6
        self.samp_rate = samp_rate = 16e6
        self.rf_freq = rf_freq = 330e6
        self.pri = pri = 1050e-6
        self.noise_power = noise_power = signal_power/pow(10, SNR/10)
        self.mod_freq = mod_freq = 10e3
        self.gain_range = gain_range = 40
        self.device = device = "device_5"
        self.carrier_freq = carrier_freq = 1e6
        self.RRC_0 = RRC_0 = firdes.root_raised_cosine(1.0, 1/pw,1/pw/2, 0.35, (11*sps))

        ##################################################
        # Blocks
        ##################################################

        self._pw_range = Range(0, 25.4e-6, 1e-6, 12.7e-6, 200)
        self._pw_win = RangeWidget(self._pw_range, self.set_pw, "'pw'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._pw_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._pri_range = Range(0, 2100e-6, 10e-6, 1050e-6, 200)
        self._pri_win = RangeWidget(self._pri_range, self.set_pri, "'pri'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._pri_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._gain_range_range = Range(0, 50, 10, 40, 200)
        self._gain_range_win = RangeWidget(self._gain_range_range, self.set_gain_range, "'gain_range'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._gain_range_win, 3, 0, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec(0))

        self.uhd_usrp_source_0.set_center_freq(rf_freq, 0)
        self.uhd_usrp_source_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_source_0.set_gain(gain_range, 0)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "receive", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(True)



        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-140, 10)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.qwidget(), Qt.QWidget)

        self.top_layout.addWidget(self._qtgui_waterfall_sink_x_0_win)
        self.qtgui_time_sink_x_1 = qtgui.time_sink_c(
            10240, #size
            samp_rate, #samp_rate
            "receive", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_1.set_update_time(0.10)
        self.qtgui_time_sink_x_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_1.enable_tags(True)
        self.qtgui_time_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_1.enable_autoscale(False)
        self.qtgui_time_sink_x_1.enable_grid(False)
        self.qtgui_time_sink_x_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_1.enable_control_panel(False)
        self.qtgui_time_sink_x_1.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_1.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_1.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_win = sip.wrapinstance(self.qtgui_time_sink_x_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_1_win)
        self.qtgui_time_sink_x_0_0 = qtgui.time_sink_c(
            102400, #size
            samp_rate, #samp_rate
            "transmit", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_win)
        self.qtgui_freq_sink_x_1 = qtgui.freq_sink_c(
            (1024*4), #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "receive", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_1.set_update_time(0.10)
        self.qtgui_freq_sink_x_1.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_1.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_1.enable_autoscale(False)
        self.qtgui_freq_sink_x_1.enable_grid(False)
        self.qtgui_freq_sink_x_1.set_fft_average(1.0)
        self.qtgui_freq_sink_x_1.enable_axis_labels(True)
        self.qtgui_freq_sink_x_1.enable_control_panel(False)
        self.qtgui_freq_sink_x_1.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_1_win = sip.wrapinstance(self.qtgui_freq_sink_x_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_1_win)
        self.qtgui_freq_sink_x_0_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "transmit", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_0.enable_grid(False)
        self.qtgui_freq_sink_x_0_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_0_win)
        self.osmosdr_sink_1 = osmosdr.sink(
            args="numchan=" + str(1) + " " + "hackrf={}".format(eval(device))
        )
        self.osmosdr_sink_1.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink_1.set_sample_rate(samp_rate)
        self.osmosdr_sink_1.set_center_freq(rf_freq, 0)
        self.osmosdr_sink_1.set_freq_corr(0, 0)
        self.osmosdr_sink_1.set_gain(11, 0)
        self.osmosdr_sink_1.set_if_gain(47, 0)
        self.osmosdr_sink_1.set_bb_gain(20, 0)
        self.osmosdr_sink_1.set_antenna('', 0)
        self.osmosdr_sink_1.set_bandwidth(0, 0)
        self.fir_filter_xxx_0_0 = filter.fir_filter_fff(1, RRC_0)
        self.fir_filter_xxx_0_0.declare_sample_delay(0)
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=(pow(noise_power*2, 1/2)),
            frequency_offset=0.0,
            epsilon=1.0,
            taps=[1],
            noise_seed=0,
            block_tags=False)
        self.blocks_vector_source_x_0_0 = blocks.vector_source_f(np.hstack((np.ones(int(pw*samp_rate)), np.zeros(int((pri-pw)*samp_rate)))), True, 1, [])
        self.blocks_vco_c_0 = blocks.vco_c(samp_rate, (carrier_freq*2*np.pi), (pow(2*signal_power, 1/2)))
        self.blocks_skiphead_0 = blocks.skiphead(gr.sizeof_gr_complex*1, int(samp_rate))
        self.blocks_multiply_xx_0_0_0_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0_0_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vff(1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(1/2)
        self.blocks_head_0 = blocks.head(gr.sizeof_gr_complex*1, int(samp_rate))
        self.blocks_float_to_complex_1 = blocks.float_to_complex(1)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, "D:/GNUradio/data/20230801/{}_nlfm".format(device), False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.blocks_add_const_vxx_0 = blocks.add_const_ff(((carrier_freq-step_freq)/1e6))
        self.analog_sig_source_x_0_0 = analog.sig_source_f(samp_rate, analog.GR_TRI_WAVE, (1/pw), (pow(step_freq/1e6,1/2)), 0, 0)
        self.analog_sig_source_x_0 = analog.sig_source_f(samp_rate, analog.GR_TRI_WAVE, (1/pw), (pow(step_freq/1e6,1/2)), 0, 0)
        self.analog_agc_xx_0 = analog.agc_cc((1e-4), 1.0, 1.0)
        self.analog_agc_xx_0.set_max_gain(65536)
        self._SNR_range = Range(-5, 15, 1, 15, 200)
        self._SNR_win = RangeWidget(self._SNR_range, self.set_SNR, "'SNR'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._SNR_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_agc_xx_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blocks_vco_c_0, 0))
        self.connect((self.blocks_complex_to_float_0, 1), (self.blocks_multiply_xx_0_0_0, 0))
        self.connect((self.blocks_complex_to_float_0, 0), (self.blocks_multiply_xx_0_0_0_0, 0))
        self.connect((self.blocks_float_to_complex_1, 0), (self.channels_channel_model_0, 0))
        self.connect((self.blocks_head_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_skiphead_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.qtgui_freq_sink_x_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.qtgui_time_sink_x_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.qtgui_waterfall_sink_x_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_add_const_vxx_0, 0))
        self.connect((self.blocks_multiply_xx_0_0_0, 0), (self.blocks_float_to_complex_1, 1))
        self.connect((self.blocks_multiply_xx_0_0_0_0, 0), (self.blocks_float_to_complex_1, 0))
        self.connect((self.blocks_skiphead_0, 0), (self.blocks_head_0, 0))
        self.connect((self.blocks_vco_c_0, 0), (self.blocks_complex_to_float_0, 0))
        self.connect((self.blocks_vector_source_x_0_0, 0), (self.fir_filter_xxx_0_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.osmosdr_sink_1, 0))
        self.connect((self.channels_channel_model_0, 0), (self.qtgui_freq_sink_x_0_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.qtgui_time_sink_x_0_0, 0))
        self.connect((self.fir_filter_xxx_0_0, 0), (self.blocks_multiply_xx_0_0_0, 1))
        self.connect((self.fir_filter_xxx_0_0, 0), (self.blocks_multiply_xx_0_0_0_0, 1))
        self.connect((self.uhd_usrp_source_0, 0), (self.analog_agc_xx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "mod_pulse_nlfm")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_device_0(self):
        return self.device_0

    def set_device_0(self, device_0):
        self.device_0 = device_0

    def get_device_1(self):
        return self.device_1

    def set_device_1(self, device_1):
        self.device_1 = device_1

    def get_device_2(self):
        return self.device_2

    def set_device_2(self, device_2):
        self.device_2 = device_2

    def get_device_3(self):
        return self.device_3

    def set_device_3(self, device_3):
        self.device_3 = device_3

    def get_device_4(self):
        return self.device_4

    def set_device_4(self, device_4):
        self.device_4 = device_4

    def get_device_5(self):
        return self.device_5

    def set_device_5(self, device_5):
        self.device_5 = device_5

    def get_device_6(self):
        return self.device_6

    def set_device_6(self, device_6):
        self.device_6 = device_6

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_RRC_0(firdes.root_raised_cosine(1.0, 1/self.pw, 1/self.pw/2, 0.35, (11*self.sps)))

    def get_signal_power(self):
        return self.signal_power

    def set_signal_power(self, signal_power):
        self.signal_power = signal_power
        self.set_noise_power(self.signal_power/pow(10, self.SNR/10))

    def get_pw(self):
        return self.pw

    def set_pw(self, pw):
        self.pw = pw
        self.set_RRC_0(firdes.root_raised_cosine(1.0, 1/self.pw, 1/self.pw/2, 0.35, (11*self.sps)))
        self.analog_sig_source_x_0.set_frequency((1/self.pw))
        self.analog_sig_source_x_0_0.set_frequency((1/self.pw))
        self.blocks_vector_source_x_0_0.set_data(np.hstack((np.ones(int(self.pw*self.samp_rate)), np.zeros(int((self.pri-self.pw)*self.samp_rate)))), [])

    def get_SNR(self):
        return self.SNR

    def set_SNR(self, SNR):
        self.SNR = SNR
        self.set_noise_power(self.signal_power/pow(10, self.SNR/10))

    def get_step_freq(self):
        return self.step_freq

    def set_step_freq(self, step_freq):
        self.step_freq = step_freq
        self.analog_sig_source_x_0.set_amplitude((pow(self.step_freq/1e6,1/2)))
        self.analog_sig_source_x_0_0.set_amplitude((pow(self.step_freq/1e6,1/2)))
        self.blocks_add_const_vxx_0.set_k(((self.carrier_freq-self.step_freq)/1e6))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate)
        self.blocks_head_0.set_length(int(self.samp_rate))
        self.blocks_vector_source_x_0_0.set_data(np.hstack((np.ones(int(self.pw*self.samp_rate)), np.zeros(int((self.pri-self.pw)*self.samp_rate)))), [])
        self.osmosdr_sink_1.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_freq_sink_x_1.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_0_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_1.set_samp_rate(self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_rf_freq(self):
        return self.rf_freq

    def set_rf_freq(self, rf_freq):
        self.rf_freq = rf_freq
        self.osmosdr_sink_1.set_center_freq(self.rf_freq, 0)
        self.uhd_usrp_source_0.set_center_freq(self.rf_freq, 0)

    def get_pri(self):
        return self.pri

    def set_pri(self, pri):
        self.pri = pri
        self.blocks_vector_source_x_0_0.set_data(np.hstack((np.ones(int(self.pw*self.samp_rate)), np.zeros(int((self.pri-self.pw)*self.samp_rate)))), [])

    def get_noise_power(self):
        return self.noise_power

    def set_noise_power(self, noise_power):
        self.noise_power = noise_power
        self.channels_channel_model_0.set_noise_voltage((pow(self.noise_power*2, 1/2)))

    def get_mod_freq(self):
        return self.mod_freq

    def set_mod_freq(self, mod_freq):
        self.mod_freq = mod_freq

    def get_gain_range(self):
        return self.gain_range

    def set_gain_range(self, gain_range):
        self.gain_range = gain_range
        self.uhd_usrp_source_0.set_gain(self.gain_range, 0)

    def get_device(self):
        return self.device

    def set_device(self, device):
        self.device = device
        self.blocks_file_sink_0.open("D:/GNUradio/data/20230801/{}_nlfm".format(self.device))

    def get_carrier_freq(self):
        return self.carrier_freq

    def set_carrier_freq(self, carrier_freq):
        self.carrier_freq = carrier_freq
        self.blocks_add_const_vxx_0.set_k(((self.carrier_freq-self.step_freq)/1e6))

    def get_RRC_0(self):
        return self.RRC_0

    def set_RRC_0(self, RRC_0):
        self.RRC_0 = RRC_0
        self.fir_filter_xxx_0_0.set_taps(self.RRC_0)



def argument_parser():
    parser = ArgumentParser()
    return parser


def main(top_block_cls=mod_pulse_nlfm, options=None):
    if options is None:
        options = argument_parser().parse_args()

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
