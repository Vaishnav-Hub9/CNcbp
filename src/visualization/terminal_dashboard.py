"""
Terminal Visualization and Reporting using Rich.
Renders side-by-side comparison tables, SLA verification, and experiment summaries.
"""

from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from src.metrics.collector import SimulationMetrics


console = Console()


def print_experiment_header(scenario_runner) -> None:
    """
    Prints a formatted summary panel of experiment parameters.
    """
    summary_text = (
        f"[bold cyan]Shared Link Bandwidth:[/bold cyan] {scenario_runner.bottleneck_bps / 1_000_000:.1f} Mbps  |  "
        f"[bold cyan]Propagation Delay:[/bold cyan] {scenario_runner.propagation_delay_sec * 1000:.1f} ms  |  "
        f"[bold cyan]Queue Buffer:[/bold cyan] {scenario_runner.buffer_packets} pkts\n"
        f"[bold yellow]Simulation Duration:[/bold yellow] {scenario_runner.duration_sec:.1f} s  |  "
        f"[bold magenta]Congestion Window:[/bold magenta] t={scenario_runner.bulk_start_time:.1f}s to t={scenario_runner.bulk_end_time:.1f}s (Bulk @ {scenario_runner.bulk_offered_mbps:.1f} Mbps)\n"
        f"[bold green]QoS Policies:[/bold green] Strict Priority Queuing (Voice/Video) + Token Bucket Shaper (Bulk @ {scenario_runner.shaper_rate_bps / 1_000_000:.1f} Mbps, Burst {scenario_runner.shaper_burst_bytes / 1024:.0f} KB)"
    )
    console.print(Panel(
        summary_text,
        title="[bold white on blue] Adaptive Bandwidth Allocation & QoS Simulator [/bold white on blue]",
        border_style="cyan",
        box=box.ROUNDED
    ))


def display_comparison_table(baseline_metrics: SimulationMetrics, qos_metrics: SimulationMetrics) -> None:
    """
    Renders a comparative side-by-side table of network metrics.
    """
    base_summary = baseline_metrics.export_summary()
    qos_summary = qos_metrics.export_summary()

    table = Table(
        title="[bold yellow]Performance Comparison: Baseline (No QoS) vs QoS-Enabled[/bold yellow]",
        box=box.HEAVY_EDGE,
        header_style="bold magenta",
        show_lines=True
    )

    table.add_column("Flow / Traffic", style="cyan", no_wrap=True)
    table.add_column("Metric", style="white")
    table.add_column("Baseline (FIFO)", justify="right", style="red")
    table.add_column("QoS Enabled", justify="right", style="green")
    table.add_column("Improvement / Delta", justify="center", style="bold yellow")

    flow_ids = list(base_summary["flows"].keys())

    for fid in flow_ids:
        b_f = base_summary["flows"][fid]
        q_f = qos_summary["flows"].get(fid, {})
        flow_label = f"{fid}\n({b_f['traffic_type']})"

        # Latency
        b_lat = b_f['avg_latency_ms']
        q_lat = q_f.get('avg_latency_ms', 0.0)
        lat_diff = b_lat - q_lat
        lat_pct = (lat_diff / b_lat * 100.0) if b_lat > 0 else 0.0
        delta_lat = f"{lat_diff:+.1f} ms ({lat_pct:.1f}% reduction)" if lat_diff > 0 else f"{lat_diff:+.1f} ms"

        # Jitter
        b_jit = b_f['avg_jitter_ms']
        q_jit = q_f.get('avg_jitter_ms', 0.0)
        jit_diff = b_jit - q_jit
        delta_jit = f"{jit_diff:+.1f} ms"

        # Loss Rate
        b_loss = b_f['loss_rate_percent']
        q_loss = q_f.get('loss_rate_percent', 0.0)
        loss_diff = b_loss - q_loss
        delta_loss = f"{loss_diff:+.1f}% drops"

        # Throughput
        b_tput = b_f['avg_throughput_mbps']
        q_tput = q_f.get('avg_throughput_mbps', 0.0)
        delta_tput = f"{q_tput - b_tput:+.2f} Mbps"

        table.add_row(flow_label, "Avg Latency (ms)", f"{b_lat:.1f} ms", f"{q_lat:.1f} ms", delta_lat)
        table.add_row("", "P95 Latency (ms)", f"{b_f['p95_latency_ms']:.1f} ms", f"{q_f.get('p95_latency_ms', 0.0):.1f} ms", "")
        table.add_row("", "Avg Jitter (ms)", f"{b_jit:.2f} ms", f"{q_jit:.2f} ms", delta_jit)
        table.add_row("", "Packet Loss (%)", f"{b_loss:.2f}%", f"{q_loss:.2f}%", delta_loss)
        table.add_row("", "Throughput (Mbps)", f"{b_tput:.2f} Mbps", f"{q_tput:.2f} Mbps", delta_tput)

    console.print(table)


def display_sla_verdict(baseline_metrics: SimulationMetrics, qos_metrics: SimulationMetrics) -> None:
    """
    Evaluates real-time Voice and Video flows against standard ITU-T G.114 telecom SLAs:
    - VoIP SLA: Latency < 150ms, Jitter < 30ms, Loss < 1.0%
    """
    base_summary = baseline_metrics.export_summary()
    qos_summary = qos_metrics.export_summary()

    voice_b = base_summary["flows"].get("voice_flow", {})
    voice_q = qos_summary["flows"].get("voice_flow", {})

    b_meets_sla = (
        voice_b.get("avg_latency_ms", 999) < 150.0 and
        voice_b.get("avg_jitter_ms", 999) < 30.0 and
        voice_b.get("loss_rate_percent", 999) < 1.0
    )

    q_meets_sla = (
        voice_q.get("avg_latency_ms", 999) < 150.0 and
        voice_q.get("avg_jitter_ms", 999) < 30.0 and
        voice_q.get("loss_rate_percent", 999) < 1.0
    )

    sla_table = Table(
        title="[bold cyan]ITU-T G.114 Real-Time Telecom Quality SLA Verification[/bold cyan]",
        box=box.ROUNDED
    )
    sla_table.add_column("Criterion", style="white")
    sla_table.add_column("VoIP Target Standard", style="cyan")
    sla_table.add_column("Baseline (No QoS)", justify="center")
    sla_table.add_column("QoS Enabled", justify="center")

    def format_status(val: float, threshold: float, unit: str, lower_is_better: bool = True):
        meets = (val <= threshold) if lower_is_better else (val >= threshold)
        color = "green" if meets else "red"
        symbol = "✓ PASS" if meets else "✗ FAIL"
        return f"[{color}]{val:.1f} {unit} ({symbol})[/{color}]"

    sla_table.add_row(
        "Voice Latency", 
        "< 150 ms",
        format_status(voice_b.get("avg_latency_ms", 0), 150.0, "ms"),
        format_status(voice_q.get("avg_latency_ms", 0), 150.0, "ms")
    )
    sla_table.add_row(
        "Voice Jitter", 
        "< 30 ms",
        format_status(voice_b.get("avg_jitter_ms", 0), 30.0, "ms"),
        format_status(voice_q.get("avg_jitter_ms", 0), 30.0, "ms")
    )
    sla_table.add_row(
        "Voice Packet Loss", 
        "< 1.0 %",
        format_status(voice_b.get("loss_rate_percent", 0), 1.0, "%"),
        format_status(voice_q.get("loss_rate_percent", 0), 1.0, "%")
    )

    console.print(sla_table)
