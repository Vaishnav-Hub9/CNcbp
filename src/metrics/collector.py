"""
Metrics Collection and Performance Analysis.
Records packet events and computes Latency, RFC 3550 Jitter, Loss Rate, and Throughput.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
from src.models.packet import Packet, TrafficType
from src.metrics.rfc3550 import RFC3550JitterCalculator


class FlowMetricsCollector:
    """
    Collects packet-level metrics for a specific traffic flow.
    """
    def __init__(self, flow_id: str, traffic_type: TrafficType):
        self.flow_id = flow_id
        self.traffic_type = traffic_type
        
        self.generated_packets: List[Packet] = []
        self.delivered_packets: List[Packet] = []
        self.dropped_packets: List[Packet] = []
        
        self.jitter_calculator = RFC3550JitterCalculator()
        self.jitter_records: List[float] = [] # Jitter per delivered packet in ms

    def on_packet_generated(self, packet: Packet) -> None:
        self.generated_packets.append(packet)

    def on_packet_delivered(self, packet: Packet) -> None:
        self.delivered_packets.append(packet)
        jitter_sec = self.jitter_calculator.record_packet(packet.created_at, packet.delivered_at)
        self.jitter_records.append(jitter_sec * 1000.0)

    def on_packet_dropped(self, packet: Packet) -> None:
        self.dropped_packets.append(packet)

    def summary(self, total_sim_time: float) -> Dict[str, Any]:
        """
        Calculates summary statistical metrics for the flow.
        """
        n_gen = len(self.generated_packets)
        n_deliv = len(self.delivered_packets)
        n_drop = len(self.dropped_packets)
        loss_pct = (n_drop / n_gen * 100.0) if n_gen > 0 else 0.0

        latencies_ms = [
            (p.delivered_at - p.created_at) * 1000.0 
            for p in self.delivered_packets 
            if p.delivered_at is not None
        ]

        queuing_delays_ms = [
            (p.service_started_at - p.enqueued_at) * 1000.0 
            for p in self.delivered_packets 
            if p.service_started_at is not None and p.enqueued_at is not None
        ]

        total_bytes_delivered = sum(p.size_bytes for p in self.delivered_packets)
        throughput_mbps = (total_bytes_delivered * 8.0) / (total_sim_time * 1_000_000.0) if total_sim_time > 0 else 0.0

        if latencies_ms:
            lat_arr = np.array(latencies_ms)
            avg_lat = float(np.mean(lat_arr))
            med_lat = float(np.median(lat_arr))
            min_lat = float(np.min(lat_arr))
            max_lat = float(np.max(lat_arr))
            p95_lat = float(np.percentile(lat_arr, 95))
            p99_lat = float(np.percentile(lat_arr, 99))
        else:
            avg_lat = med_lat = min_lat = max_lat = p95_lat = p99_lat = 0.0

        if self.jitter_records:
            jit_arr = np.array(self.jitter_records)
            avg_jit = float(np.mean(jit_arr))
            max_jit = float(np.max(jit_arr))
            p95_jit = float(np.percentile(jit_arr, 95))
        else:
            avg_jit = max_jit = p95_jit = 0.0

        return {
            "flow_id": self.flow_id,
            "traffic_type": self.traffic_type.value,
            "packets_generated": n_gen,
            "packets_delivered": n_deliv,
            "packets_dropped": n_drop,
            "loss_rate_percent": round(loss_pct, 2),
            "avg_latency_ms": round(avg_lat, 2),
            "median_latency_ms": round(med_lat, 2),
            "min_latency_ms": round(min_lat, 2),
            "max_latency_ms": round(max_lat, 2),
            "p95_latency_ms": round(p95_lat, 2),
            "p99_latency_ms": round(p99_lat, 2),
            "avg_queuing_delay_ms": round(float(np.mean(queuing_delays_ms)) if queuing_delays_ms else 0.0, 2),
            "avg_jitter_ms": round(avg_jit, 2),
            "max_jitter_ms": round(max_jit, 2),
            "p95_jitter_ms": round(p95_jit, 2),
            "total_mbytes_delivered": round(total_bytes_delivered / (1024 * 1024), 2),
            "avg_throughput_mbps": round(throughput_mbps, 3),
        }


class SimulationMetrics:
    """
    Coordinates metrics collection across all flows and the shared network link.
    """
    def __init__(self, run_name: str, total_time: float):
        self.run_name = run_name
        self.total_time = total_time
        self.flow_collectors: Dict[str, FlowMetricsCollector] = {}
        
        # Periodic samples for time-series visualization
        self.queue_occupancy_samples: List[Dict[str, Any]] = [] # {time, total_packets, high_packets, low_packets}

    def get_flow_collector(self, flow_id: str, traffic_type: TrafficType) -> FlowMetricsCollector:
        if flow_id not in self.flow_collectors:
            self.flow_collectors[flow_id] = FlowMetricsCollector(flow_id, traffic_type)
        return self.flow_collectors[flow_id]

    def record_queue_sample(self, current_time: float, total_packets: int, high_packets: int = 0, low_packets: int = 0) -> None:
        self.queue_occupancy_samples.append({
            "time": current_time,
            "total_packets": total_packets,
            "high_packets": high_packets,
            "low_packets": low_packets
        })

    def get_throughput_series(self, flow_id: str, bin_size_sec: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns (time_bins, throughput_mbps) for the given flow.
        """
        collector = self.flow_collectors.get(flow_id)
        if not collector or not collector.delivered_packets:
            return np.array([]), np.array([])

        num_bins = int(np.ceil(self.total_time / bin_size_sec))
        bins = np.linspace(0, self.total_time, num_bins + 1)
        byte_counts = np.zeros(num_bins)

        for p in collector.delivered_packets:
            if p.delivered_at is not None and p.delivered_at <= self.total_time:
                b_idx = int(p.delivered_at // bin_size_sec)
                if 0 <= b_idx < num_bins:
                    byte_counts[b_idx] += p.size_bytes

        # Convert bytes in bin to Mbps: (bytes * 8) / (bin_size * 1,000,000)
        throughput_mbps = (byte_counts * 8.0) / (bin_size_sec * 1_000_000.0)
        time_midpoints = bins[:-1] + (bin_size_sec / 2.0)
        return time_midpoints, throughput_mbps

    def export_summary(self) -> Dict[str, Any]:
        """
        Aggregates summary statistics for all flows and overall run.
        """
        flow_summaries = {}
        total_gen = 0
        total_deliv = 0
        total_drop = 0
        total_bytes = 0

        for fid, col in self.flow_collectors.items():
            f_sum = col.summary(self.total_time)
            flow_summaries[fid] = f_sum
            total_gen += f_sum["packets_generated"]
            total_deliv += f_sum["packets_delivered"]
            total_drop += f_sum["packets_dropped"]
            total_bytes += sum(p.size_bytes for p in col.delivered_packets)

        overall_loss_pct = (total_drop / total_gen * 100.0) if total_gen > 0 else 0.0
        overall_throughput_mbps = (total_bytes * 8.0) / (self.total_time * 1_000_000.0) if self.total_time > 0 else 0.0

        return {
            "run_name": self.run_name,
            "total_simulation_time_sec": self.total_time,
            "overall_packets_generated": total_gen,
            "overall_packets_delivered": total_deliv,
            "overall_packets_dropped": total_drop,
            "overall_loss_rate_percent": round(overall_loss_pct, 2),
            "overall_throughput_mbps": round(overall_throughput_mbps, 3),
            "flows": flow_summaries
        }

    def to_dataframe(self) -> pd.DataFrame:
        """
        Converts all delivered packet records to a pandas DataFrame.
        """
        records = []
        for fid, col in self.flow_collectors.items():
            for p in col.delivered_packets:
                records.append({
                    "packet_id": p.packet_id,
                    "flow_id": p.flow_id,
                    "traffic_type": p.traffic_type.value,
                    "size_bytes": p.size_bytes,
                    "created_at": p.created_at,
                    "enqueued_at": p.enqueued_at,
                    "delivered_at": p.delivered_at,
                    "latency_ms": (p.delivered_at - p.created_at) * 1000.0 if p.delivered_at else None,
                    "dropped": False
                })
            for p in col.dropped_packets:
                records.append({
                    "packet_id": p.packet_id,
                    "flow_id": p.flow_id,
                    "traffic_type": p.traffic_type.value,
                    "size_bytes": p.size_bytes,
                    "created_at": p.created_at,
                    "enqueued_at": p.enqueued_at,
                    "delivered_at": None,
                    "latency_ms": None,
                    "dropped": True
                })
        return pd.DataFrame(records)
