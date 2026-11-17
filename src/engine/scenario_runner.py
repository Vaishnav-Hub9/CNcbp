"""
Scenario Runner for Comparative Dual-Run Experiments (Baseline vs QoS).
Ensures 100% fair evaluation by replaying an identical packet stream through both systems.
"""

import copy
from typing import List, Tuple, Dict, Any
from src.models.packet import Packet, TrafficType, PriorityLevel
from src.models.flow import (
    FlowConfig,
    VoiceTrafficGenerator,
    VideoTrafficGenerator,
    BulkTrafficGenerator
)
from src.algorithms.fifo_queue import FIFOQueue
from src.algorithms.priority_queue import PriorityQueueScheduler
from src.algorithms.token_bucket import TokenBucketShaper
from src.engine.discrete_event_sim import DiscreteEventSimulator
from src.metrics.collector import SimulationMetrics


class ScenarioRunner:
    """
    Sets up and executes the standard multi-flow congestion experiment.
    """
    def __init__(
        self,
        duration_sec: float = 30.0,
        bottleneck_mbps: float = 10.0,
        propagation_delay_ms: float = 5.0,
        bulk_start_time: float = 5.0,
        bulk_end_time: float = 25.0,
        bulk_offered_mbps: float = 15.0,
        shaper_rate_mbps: float = 6.0,
        shaper_burst_kb: float = 30.0,
        buffer_packets: int = 100,
        random_seed: int = 42
    ):
        self.duration_sec = duration_sec
        self.bottleneck_bps = bottleneck_mbps * 1_000_000.0
        self.propagation_delay_sec = propagation_delay_ms / 1000.0
        self.bulk_start_time = bulk_start_time
        self.bulk_end_time = bulk_end_time
        self.bulk_offered_mbps = bulk_offered_mbps
        self.shaper_rate_bps = shaper_rate_mbps * 1_000_000.0
        self.shaper_burst_bytes = int(shaper_burst_kb * 1024)
        self.buffer_packets = buffer_packets
        self.random_seed = random_seed

    def generate_traffic(self) -> List[Packet]:
        """
        Generates synthetic traffic for Voice, Video, and Bulk flows.
        """
        # 1. Voice Flow (Active 0s to end)
        voice_cfg = FlowConfig(
            flow_id="voice_flow",
            traffic_type=TrafficType.VOICE,
            priority=PriorityLevel.HIGH,
            dscp_tag="EF",
            start_time=0.0,
            end_time=self.duration_sec
        )
        voice_gen = VoiceTrafficGenerator(voice_cfg, interval=0.020, packet_size=200, seed=self.random_seed)
        voice_packets = voice_gen.generate(start_id=1)

        # 2. Video Flow (Active 0s to end)
        video_cfg = FlowConfig(
            flow_id="video_flow",
            traffic_type=TrafficType.VIDEO,
            priority=PriorityLevel.HIGH,
            dscp_tag="AF41",
            start_time=0.0,
            end_time=self.duration_sec
        )
        video_gen = VideoTrafficGenerator(video_cfg, fps=30, seed=self.random_seed + 1)
        video_packets = video_gen.generate(start_id=100000)

        # 3. Bulk Download Flow (Active bulk_start_time to bulk_end_time)
        bulk_cfg = FlowConfig(
            flow_id="bulk_download",
            traffic_type=TrafficType.BULK,
            priority=PriorityLevel.LOW,
            dscp_tag="CS0",
            start_time=self.bulk_start_time,
            end_time=self.bulk_end_time
        )
        bulk_gen = BulkTrafficGenerator(
            bulk_cfg, 
            offered_rate_mbps=self.bulk_offered_mbps, 
            seed=self.random_seed + 2
        )
        bulk_packets = bulk_gen.generate(start_id=500000)

        all_packets = voice_packets + video_packets + bulk_packets
        all_packets.sort(key=lambda p: p.created_at)
        return all_packets

    def run_experiment(self) -> Tuple[SimulationMetrics, SimulationMetrics, List[Packet]]:
        """
        Runs Run A (Baseline FIFO) and Run B (QoS Priority + Shaping) on identical packets.
        Returns (baseline_metrics, qos_metrics, original_packets).
        """
        master_packets = self.generate_traffic()

        # Run A: Baseline FIFO
        packets_run_a = copy.deepcopy(master_packets)
        fifo_queue = FIFOQueue(max_packets=self.buffer_packets)
        sim_baseline = DiscreteEventSimulator(
            link_bandwidth_bps=self.bottleneck_bps,
            propagation_delay_sec=self.propagation_delay_sec,
            queue_manager=fifo_queue,
            run_name="Run A (No QoS / Baseline FIFO)",
            total_time_sec=self.duration_sec
        )
        sim_baseline.load_packets(packets_run_a)
        baseline_metrics = sim_baseline.run()

        # Run B: QoS Priority Queuing + Token Bucket Shaping
        packets_run_b = copy.deepcopy(master_packets)
        token_shaper = TokenBucketShaper(
            rate_bps=self.shaper_rate_bps,
            capacity_bytes=self.shaper_burst_bytes
        )
        qos_scheduler = PriorityQueueScheduler(
            high_max_packets=self.buffer_packets,
            low_max_packets=self.buffer_packets,
            shaper=token_shaper
        )
        sim_qos = DiscreteEventSimulator(
            link_bandwidth_bps=self.bottleneck_bps,
            propagation_delay_sec=self.propagation_delay_sec,
            queue_manager=qos_scheduler,
            run_name="Run B (QoS-Enabled: Priority + Shaping)",
            total_time_sec=self.duration_sec
        )
        sim_qos.load_packets(packets_run_b)
        qos_metrics = sim_qos.run()

        return baseline_metrics, qos_metrics, master_packets
