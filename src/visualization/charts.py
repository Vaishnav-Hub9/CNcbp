"""
Publication-Quality Network Performance Visualizations.
Generates side-by-side comparison charts for Latency, Jitter, Packet Loss, and Throughput.
"""

import os
from typing import Optional
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from src.metrics.collector import SimulationMetrics


def set_plotting_style():
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    plt.rcParams.update({
        'font.sans-serif': 'DejaVu Sans',
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 13,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 11,
        'figure.titlesize': 15,
        'figure.dpi': 300
    })


def generate_all_plots(
    baseline_metrics: SimulationMetrics,
    qos_metrics: SimulationMetrics,
    output_dir: str = "results",
    bulk_start: float = 5.0,
    bulk_end: float = 25.0
) -> None:
    """
    Produces all comparison charts and saves them to output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    set_plotting_style()

    # 1. Latency Comparison Chart
    plot_latency_comparison(baseline_metrics, qos_metrics, output_dir, bulk_start, bulk_end)

    # 2. Jitter Comparison Chart
    plot_jitter_comparison(baseline_metrics, qos_metrics, output_dir, bulk_start, bulk_end)

    # 3. Packet Loss Comparison Chart
    plot_packet_loss_comparison(baseline_metrics, qos_metrics, output_dir, bulk_start, bulk_end)

    # 4. Throughput Comparison Chart
    plot_throughput_comparison(baseline_metrics, qos_metrics, output_dir, bulk_start, bulk_end)

    # 5. Comprehensive Executive Dashboard
    plot_executive_dashboard(baseline_metrics, qos_metrics, output_dir, bulk_start, bulk_end)

    # 6. Summary Metrics Bar Chart
    plot_summary_bars(baseline_metrics, qos_metrics, output_dir)


def plot_latency_comparison(
    baseline: SimulationMetrics, 
    qos: SimulationMetrics, 
    output_dir: str, 
    bulk_start: float, 
    bulk_end: float
) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True, sharey=True)

    # Top: Baseline FIFO
    ax1 = axes[0]
    ax1.axvspan(bulk_start, bulk_end, color='red', alpha=0.12, label='Congestion Period (Bulk Download Active)')
    
    b_voice = baseline.flow_collectors.get("voice_flow")
    if b_voice:
        t_v = [p.delivered_at for p in b_voice.delivered_packets]
        lat_v = [(p.delivered_at - p.created_at) * 1000.0 for p in b_voice.delivered_packets]
        ax1.scatter(t_v, lat_v, color='#d62728', s=12, alpha=0.7, label='Voice (Baseline FIFO)')

    b_vid = baseline.flow_collectors.get("video_flow")
    if b_vid:
        t_vid = [p.delivered_at for p in b_vid.delivered_packets]
        lat_vid = [(p.delivered_at - p.created_at) * 1000.0 for p in b_vid.delivered_packets]
        ax1.scatter(t_vid, lat_vid, color='#ff7f0e', s=8, alpha=0.4, label='Video (Baseline FIFO)')

    ax1.set_title("Run A: Baseline (Best-Effort FIFO) — Severe Latency Spikes Under Congestion", fontweight='bold')
    ax1.set_ylabel("Latency (ms)")
    ax1.legend(loc='upper right', frameon=True)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Bottom: QoS Enabled
    ax2 = axes[1]
    ax2.axvspan(bulk_start, bulk_end, color='green', alpha=0.08, label='Congestion Period (QoS Active)')

    q_voice = qos.flow_collectors.get("voice_flow")
    if q_voice:
        t_v = [p.delivered_at for p in q_voice.delivered_packets]
        lat_v = [(p.delivered_at - p.created_at) * 1000.0 for p in q_voice.delivered_packets]
        ax2.scatter(t_v, lat_v, color='#2ca02c', s=12, alpha=0.7, label='Voice (QoS Priority Queue)')

    q_vid = qos.flow_collectors.get("video_flow")
    if q_vid:
        t_vid = [p.delivered_at for p in q_vid.delivered_packets]
        lat_vid = [(p.delivered_at - p.created_at) * 1000.0 for p in q_vid.delivered_packets]
        ax2.scatter(t_vid, lat_vid, color='#1f77b4', s=8, alpha=0.4, label='Video (QoS Priority Queue)')

    ax2.set_title("Run B: QoS-Enabled (Priority Queuing + Shaping) — Flat, Stable Real-Time Latency", fontweight='bold')
    ax2.set_xlabel("Simulation Time (seconds)")
    ax2.set_ylabel("Latency (ms)")
    ax2.legend(loc='upper right', frameon=True)
    ax2.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "latency_comparison.png"), dpi=300)
    plt.close()


def plot_jitter_comparison(
    baseline: SimulationMetrics, 
    qos: SimulationMetrics, 
    output_dir: str, 
    bulk_start: float, 
    bulk_end: float
) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.axvspan(bulk_start, bulk_end, color='gray', alpha=0.15, label='Bulk Congestion Period')
    ax.axhline(30.0, color='red', linestyle='--', linewidth=1.8, label='ITU-T G.114 Jitter Tolerance Threshold (30 ms)')

    # Baseline Voice Jitter
    b_voice = baseline.flow_collectors.get("voice_flow")
    if b_voice and b_voice.jitter_records:
        times = [p.delivered_at for p in b_voice.delivered_packets]
        ax.plot(times, b_voice.jitter_records, color='#d62728', linewidth=2.0, label='Voice Jitter (Baseline FIFO)')

    # QoS Voice Jitter
    q_voice = qos.flow_collectors.get("voice_flow")
    if q_voice and q_voice.jitter_records:
        times = [p.delivered_at for p in q_voice.delivered_packets]
        ax.plot(times, q_voice.jitter_records, color='#2ca02c', linewidth=2.2, label='Voice Jitter (QoS Enabled)')

    ax.set_title("Voice Interarrival Jitter (RFC 3550): Baseline vs QoS-Enabled", fontweight='bold')
    ax.set_xlabel("Simulation Time (seconds)")
    ax.set_ylabel("RFC 3550 Jitter (ms)")
    ax.legend(loc='upper right', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "jitter_comparison.png"), dpi=300)
    plt.close()


def plot_packet_loss_comparison(
    baseline: SimulationMetrics, 
    qos: SimulationMetrics, 
    output_dir: str, 
    bulk_start: float, 
    bulk_end: float
) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.axvspan(bulk_start, bulk_end, color='gray', alpha=0.15, label='Bulk Congestion Period')

    # Cumulative drops over time
    def get_cumulative_drops(sim_metrics: SimulationMetrics, flow_id: str):
        col = sim_metrics.flow_collectors.get(flow_id)
        if not col or not col.dropped_packets:
            return [0.0, sim_metrics.total_time], [0, 0]
        times = sorted([p.enqueued_at if p.enqueued_at else p.created_at for p in col.dropped_packets])
        counts = list(range(1, len(times) + 1))
        return [0.0] + times, [0] + counts

    t_b_v, c_b_v = get_cumulative_drops(baseline, "voice_flow")
    t_b_vid, c_b_vid = get_cumulative_drops(baseline, "video_flow")
    t_q_v, c_q_v = get_cumulative_drops(qos, "voice_flow")
    t_q_vid, c_q_vid = get_cumulative_drops(qos, "video_flow")

    ax.step(t_b_v, c_b_v, color='#d62728', linewidth=2.2, label=f'Voice Drops - Baseline (Total: {c_b_v[-1]})')
    ax.step(t_b_vid, c_b_vid, color='#ff7f0e', linewidth=2.0, linestyle='-.', label=f'Video Drops - Baseline (Total: {c_b_vid[-1]})')
    ax.step(t_q_v, c_q_v, color='#2ca02c', linewidth=2.5, label=f'Voice Drops - QoS (Total: {c_q_v[-1]})')
    ax.step(t_q_vid, c_q_vid, color='#1f77b4', linewidth=2.2, linestyle=':', label=f'Video Drops - QoS (Total: {c_q_vid[-1]})')

    ax.set_title("Cumulative Real-Time Packet Loss Over Time", fontweight='bold')
    ax.set_xlabel("Simulation Time (seconds)")
    ax.set_ylabel("Total Dropped Packets")
    ax.legend(loc='upper left', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "packet_loss_comparison.png"), dpi=300)
    plt.close()


def plot_throughput_comparison(
    baseline: SimulationMetrics, 
    qos: SimulationMetrics, 
    output_dir: str, 
    bulk_start: float, 
    bulk_end: float
) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True, sharey=True)

    # Baseline Throughput
    ax1 = axes[0]
    ax1.axvspan(bulk_start, bulk_end, color='red', alpha=0.1, label='Bulk Congestion Period')
    t_bins, tp_bulk = baseline.get_throughput_series("bulk_download")
    _, tp_vid = baseline.get_throughput_series("video_flow")
    _, tp_voice = baseline.get_throughput_series("voice_flow")

    if len(t_bins) > 0:
        ax1.plot(t_bins, tp_bulk, color='purple', label='Bulk Download (Unshaped, Monopolizes Link)', linewidth=2)
        ax1.plot(t_bins, tp_vid, color='orange', label='Video Stream', linewidth=2)
        ax1.plot(t_bins, tp_voice, color='red', label='Voice Call', linewidth=2)

    ax1.set_title("Baseline Throughput: Bulk Download Consumes Entire Link Bandwidth", fontweight='bold')
    ax1.set_ylabel("Throughput (Mbps)")
    ax1.legend(loc='upper right', frameon=True)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # QoS Throughput
    ax2 = axes[1]
    ax2.axvspan(bulk_start, bulk_end, color='green', alpha=0.1, label='Bulk Congestion Period')
    t_bins_q, tp_bulk_q = qos.get_throughput_series("bulk_download")
    _, tp_vid_q = qos.get_throughput_series("video_flow")
    _, tp_voice_q = qos.get_throughput_series("voice_flow")

    if len(t_bins_q) > 0:
        ax2.plot(t_bins_q, tp_bulk_q, color='purple', linestyle='--', label='Bulk Download (Shaped to ~6 Mbps)', linewidth=2)
        ax2.plot(t_bins_q, tp_vid_q, color='blue', label='Video Stream (Protected)', linewidth=2)
        ax2.plot(t_bins_q, tp_voice_q, color='green', label='Voice Call (Protected)', linewidth=2)

    ax2.set_title("QoS Throughput: Token Bucket Shapes Bulk, Leaving Headroom for Real-Time", fontweight='bold')
    ax2.set_xlabel("Simulation Time (seconds)")
    ax2.set_ylabel("Throughput (Mbps)")
    ax2.legend(loc='upper right', frameon=True)
    ax2.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "throughput_comparison.png"), dpi=300)
    plt.close()


def plot_executive_dashboard(
    baseline: SimulationMetrics, 
    qos: SimulationMetrics, 
    output_dir: str, 
    bulk_start: float, 
    bulk_end: float
) -> None:
    """
    Produces a single 4-panel executive dashboard summarizing all primary findings.
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle("Adaptive QoS vs Baseline (Best-Effort) Performance Dashboard", fontsize=16, fontweight='bold', y=0.98)

    # 1. Voice Latency
    ax1.axvspan(bulk_start, bulk_end, color='gray', alpha=0.15)
    b_voice = baseline.flow_collectors.get("voice_flow")
    q_voice = qos.flow_collectors.get("voice_flow")

    if b_voice:
        t_b = [p.delivered_at for p in b_voice.delivered_packets]
        lat_b = [(p.delivered_at - p.created_at) * 1000.0 for p in b_voice.delivered_packets]
        ax1.scatter(t_b, lat_b, color='#d62728', s=10, alpha=0.6, label='Baseline (FIFO)')

    if q_voice:
        t_q = [p.delivered_at for p in q_voice.delivered_packets]
        lat_q = [(p.delivered_at - p.created_at) * 1000.0 for p in q_voice.delivered_packets]
        ax1.scatter(t_q, lat_q, color='#2ca02c', s=10, alpha=0.7, label='QoS Enabled')

    ax1.set_title("Voice Packet Latency Over Time", fontweight='bold')
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Latency (ms)")
    ax1.legend(frameon=True)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # 2. Voice Jitter
    ax2.axvspan(bulk_start, bulk_end, color='gray', alpha=0.15)
    ax2.axhline(30.0, color='red', linestyle='--', linewidth=1.5, label='ITU-T Limit (30ms)')

    if b_voice and b_voice.jitter_records:
        t_b_j = [p.delivered_at for p in b_voice.delivered_packets]
        ax2.plot(t_b_j, b_voice.jitter_records, color='#d62728', linewidth=2, label='Baseline (Spikes!)')

    if q_voice and q_voice.jitter_records:
        t_q_j = [p.delivered_at for p in q_voice.delivered_packets]
        ax2.plot(t_q_j, q_voice.jitter_records, color='#2ca02c', linewidth=2.2, label='QoS (Smooth)')

    ax2.set_title("Voice Interarrival Jitter (RFC 3550)", fontweight='bold')
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Jitter (ms)")
    ax2.legend(frameon=True)
    ax2.grid(True, linestyle='--', alpha=0.5)

    # 3. Queue Occupancy Over Time
    b_q_samples = baseline.queue_occupancy_samples
    q_q_samples = qos.queue_occupancy_samples

    if b_q_samples:
        t_bq = [s["time"] for s in b_q_samples]
        n_bq = [s["total_packets"] for s in b_q_samples]
        ax3.plot(t_bq, n_bq, color='#d62728', label='Baseline FIFO Buffer Occupancy')

    if q_q_samples:
        t_qq = [s["time"] for s in q_q_samples]
        n_hq = [s["high_packets"] for s in q_q_samples]
        n_lq = [s["low_packets"] for s in q_q_samples]
        ax3.plot(t_qq, n_hq, color='#2ca02c', linewidth=2, label='QoS High-Priority Queue (Empty/Near Zero)')
        ax3.plot(t_qq, n_lq, color='purple', linestyle=':', label='QoS Low-Priority Queue (Buffer Bulk)')

    ax3.set_title("Queue Occupancy (Packets Waiting)", fontweight='bold')
    ax3.set_xlabel("Time (s)")
    ax3.set_ylabel("Buffered Packets")
    ax3.legend(frameon=True)
    ax3.grid(True, linestyle='--', alpha=0.5)

    # 4. Summary Bar Chart of Loss Rate
    flows = ['Voice', 'Video', 'Bulk']
    base_loss = [
        baseline.flow_collectors['voice_flow'].summary(baseline.total_time)['loss_rate_percent'],
        baseline.flow_collectors['video_flow'].summary(baseline.total_time)['loss_rate_percent'],
        baseline.flow_collectors['bulk_download'].summary(baseline.total_time)['loss_rate_percent'],
    ]
    qos_loss = [
        qos.flow_collectors['voice_flow'].summary(qos.total_time)['loss_rate_percent'],
        qos.flow_collectors['video_flow'].summary(qos.total_time)['loss_rate_percent'],
        qos.flow_collectors['bulk_download'].summary(qos.total_time)['loss_rate_percent'],
    ]

    x = np.arange(len(flows))
    width = 0.35

    ax4.bar(x - width/2, base_loss, width, label='Baseline Loss %', color='#d62728', alpha=0.85)
    ax4.bar(x + width/2, qos_loss, width, label='QoS Loss %', color='#2ca02c', alpha=0.85)

    ax4.set_title("Packet Loss Percentage Comparison", fontweight='bold')
    ax4.set_ylabel("Loss Rate (%)")
    ax4.set_xticks(x)
    ax4.set_xticklabels(flows)
    ax4.legend(frameon=True)
    ax4.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "executive_dashboard.png"), dpi=300)
    plt.close()


def plot_summary_bars(baseline: SimulationMetrics, qos: SimulationMetrics, output_dir: str) -> None:
    """
    Renders bar charts for Latency and Jitter comparison.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    flows = ['Voice', 'Video']
    base_lat = [
        baseline.flow_collectors['voice_flow'].summary(baseline.total_time)['avg_latency_ms'],
        baseline.flow_collectors['video_flow'].summary(baseline.total_time)['avg_latency_ms'],
    ]
    qos_lat = [
        qos.flow_collectors['voice_flow'].summary(qos.total_time)['avg_latency_ms'],
        qos.flow_collectors['video_flow'].summary(qos.total_time)['avg_latency_ms'],
    ]

    x = np.arange(len(flows))
    width = 0.35

    ax1.bar(x - width/2, base_lat, width, label='Baseline (FIFO)', color='#d62728', alpha=0.85)
    ax1.bar(x + width/2, qos_lat, width, label='QoS Enabled', color='#2ca02c', alpha=0.85)
    ax1.set_title("Average Latency (ms)", fontweight='bold')
    ax1.set_ylabel("ms")
    ax1.set_xticks(x)
    ax1.set_xticklabels(flows)
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.5)

    base_jit = [
        baseline.flow_collectors['voice_flow'].summary(baseline.total_time)['avg_jitter_ms'],
        baseline.flow_collectors['video_flow'].summary(baseline.total_time)['avg_jitter_ms'],
    ]
    qos_jit = [
        qos.flow_collectors['voice_flow'].summary(qos.total_time)['avg_jitter_ms'],
        qos.flow_collectors['video_flow'].summary(qos.total_time)['avg_jitter_ms'],
    ]

    ax2.bar(x - width/2, base_jit, width, label='Baseline (FIFO)', color='#d62728', alpha=0.85)
    ax2.bar(x + width/2, qos_jit, width, label='QoS Enabled', color='#2ca02c', alpha=0.85)
    ax2.set_title("Average Jitter (ms)", fontweight='bold')
    ax2.set_ylabel("ms")
    ax2.set_xticks(x)
    ax2.set_xticklabels(flows)
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "summary_bar_chart.png"), dpi=300)
    plt.close()
