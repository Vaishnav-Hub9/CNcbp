#!/usr/bin/env python3
"""
Adaptive Bandwidth Allocation & QoS Simulator for Mixed Network Traffic
Main Execution Entry Point.
"""

import argparse
import json
import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from src.engine.scenario_runner import ScenarioRunner
from src.visualization.terminal_dashboard import (
    print_experiment_header,
    display_comparison_table,
    display_sla_verdict
)
from src.visualization.charts import generate_all_plots


console = Console()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Adaptive Bandwidth Allocation & QoS Simulator for Mixed Network Traffic (Voice, Video, Bulk)"
    )
    parser.add_argument(
        "--duration", type=float, default=30.0,
        help="Total simulation duration in seconds (default: 30.0)"
    )
    parser.add_argument(
        "--link-mbps", type=float, default=10.0,
        help="Bottleneck link capacity in Mbps (default: 10.0)"
    )
    parser.add_argument(
        "--propagation-ms", type=float, default=5.0,
        help="Link propagation delay in milliseconds (default: 5.0)"
    )
    parser.add_argument(
        "--bulk-start", type=float, default=5.0,
        help="Time in seconds when bulk download begins (default: 5.0)"
    )
    parser.add_argument(
        "--bulk-end", type=float, default=25.0,
        help="Time in seconds when bulk download ends (default: 25.0)"
    )
    parser.add_argument(
        "--bulk-mbps", type=float, default=15.0,
        help="Offered load of the bulk download in Mbps (default: 15.0)"
    )
    parser.add_argument(
        "--shaper-mbps", type=float, default=6.0,
        help="Token bucket sustained rate limit for bulk traffic in Mbps (default: 6.0)"
    )
    parser.add_argument(
        "--shaper-burst-kb", type=float, default=30.0,
        help="Token bucket burst depth in Kilobytes (default: 30.0)"
    )
    parser.add_argument(
        "--buffer-size", type=int, default=100,
        help="Queue buffer limit in packets (default: 100)"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for deterministic, reproducible simulation (default: 42)"
    )
    parser.add_argument(
        "--output-dir", type=str, default="results",
        help="Directory to save generated charts, CSVs, and JSON reports (default: results)"
    )
    parser.add_argument(
        "--no-plots", action="store_true",
        help="Skip generating graphical image charts (terminal output only)"
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    os.makedirs(args.output_dir, exist_ok=True)

    console.print("\n[bold cyan]================================================================================[/bold cyan]")
    console.print("[bold yellow]       ADAPTIVE BANDWIDTH ALLOCATION & QOS SIMULATOR       [/bold yellow]")
    console.print("[bold cyan]================================================================================[/bold cyan]\n")

    runner = ScenarioRunner(
        duration_sec=args.duration,
        bottleneck_mbps=args.link_mbps,
        propagation_delay_ms=args.propagation_ms,
        bulk_start_time=args.bulk_start,
        bulk_end_time=args.bulk_end,
        bulk_offered_mbps=args.bulk_mbps,
        shaper_rate_mbps=args.shaper_mbps,
        shaper_burst_kb=args.shaper_burst_kb,
        buffer_packets=args.buffer_size,
        random_seed=args.seed
    )

    print_experiment_header(runner)
    console.print("")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task1 = progress.add_task("[cyan]Generating synthetic network traffic...", total=100)
        progress.update(task1, advance=40)
        time.sleep(0.1)

        task2 = progress.add_task("[yellow]Simulating Run A: Baseline (Best-Effort FIFO)...", total=100)
        task3 = progress.add_task("[green]Simulating Run B: QoS-Enabled (Priority + Shaping)...", total=100)

        # Run both simulations
        progress.update(task1, completed=100)
        progress.update(task2, advance=30)

        baseline_metrics, qos_metrics, packets = runner.run_experiment()
        progress.update(task2, completed=100)
        progress.update(task3, completed=100)

    console.print("\n[bold green]✓ Simulation completed successfully![/bold green]\n")

    # Display comparison tables
    display_comparison_table(baseline_metrics, qos_metrics)
    console.print("")
    display_sla_verdict(baseline_metrics, qos_metrics)
    console.print("")

    # Export CSVs & JSON summaries
    df_baseline = baseline_metrics.to_dataframe()
    df_qos = qos_metrics.to_dataframe()

    baseline_csv = os.path.join(args.output_dir, "baseline_packet_trace.csv")
    qos_csv = os.path.join(args.output_dir, "qos_packet_trace.csv")
    df_baseline.to_csv(baseline_csv, index=False)
    df_qos.to_csv(qos_csv, index=False)

    summary_data = {
        "parameters": vars(args),
        "baseline_summary": baseline_metrics.export_summary(),
        "qos_summary": qos_metrics.export_summary(),
    }
    summary_json_path = os.path.join(args.output_dir, "summary_metrics.json")
    with open(summary_json_path, "w") as f:
        json.dump(summary_data, f, indent=2)

    console.print(f"[bold cyan]Data Traces Saved:[/bold cyan]")
    console.print(f"  • Baseline trace: [white]{baseline_csv}[/white] ({len(df_baseline):,} packets)")
    console.print(f"  • QoS trace:      [white]{qos_csv}[/white] ({len(df_qos):,} packets)")
    console.print(f"  • Summary JSON:   [white]{summary_json_path}[/white]")

    # Generate charts
    if not args.no_plots:
        console.print(f"\n[cyan]Generating high-resolution comparative figures in '{args.output_dir}'...[/cyan]")
        generate_all_plots(
            baseline_metrics,
            qos_metrics,
            output_dir=args.output_dir,
            bulk_start=args.bulk_start,
            bulk_end=args.bulk_end
        )
        console.print(f"[bold green]✓ Figures saved in [white]{os.path.abspath(args.output_dir)}[/white]:[/bold green]")
        console.print("  • executive_dashboard.png     (4-panel executive summary)")
        console.print("  • latency_comparison.png       (Voice & Video latency vs time)")
        console.print("  • jitter_comparison.png        (RFC 3550 Jitter vs 30ms ITU-T limit)")
        console.print("  • packet_loss_comparison.png   (Cumulative drop count over time)")
        console.print("  • throughput_comparison.png    (Bandwidth allocation over time)")
        console.print("  • summary_bar_chart.png        (Aggregate metric bars)")

    console.print("\n[bold green]Ready for review and presentation![/bold green]\n")


if __name__ == "__main__":
    main()
