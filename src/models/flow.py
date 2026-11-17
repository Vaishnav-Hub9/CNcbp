"""
Traffic Flow Generators for Voice, Video, and Bulk Data.
Produces realistic synthetic network traffic packet streams.
"""

import random
from dataclasses import dataclass
from typing import List, Generator
from src.models.packet import Packet, TrafficType, PriorityLevel


@dataclass
class FlowConfig:
    flow_id: str
    traffic_type: TrafficType
    priority: PriorityLevel
    dscp_tag: str
    start_time: float   # seconds
    end_time: float     # seconds


class VoiceTrafficGenerator:
    """
    Simulates VoIP / Voice call traffic (e.g., Opus / G.711 codec).
    Characteristics:
    - Fixed packet intervals (typically 20ms = 50 packets/sec).
    - Small packet size: 160-byte payload + 40-byte IP/UDP/RTP headers = 200 bytes.
    - Constant Bit Rate (CBR): ~80 kbps.
    - Highest sensitivity to delay and jitter.
    """
    def __init__(self, config: FlowConfig, interval: float = 0.020, packet_size: int = 200, seed: int = 42):
        self.config = config
        self.interval = interval          # 20ms
        self.packet_size = packet_size    # 200 bytes
        self.random = random.Random(seed)

    def generate(self, start_id: int = 1) -> List[Packet]:
        packets: List[Packet] = []
        current_time = self.config.start_time
        pkt_id = start_id

        while current_time <= self.config.end_time:
            # Add minor micro-jitter in sender packetization (+/- 0.5ms)
            actual_time = max(self.config.start_time, current_time + self.random.uniform(-0.0005, 0.0005))
            pkt = Packet(
                packet_id=pkt_id,
                flow_id=self.config.flow_id,
                traffic_type=self.config.traffic_type,
                size_bytes=self.packet_size,
                created_at=actual_time,
                priority=self.config.priority,
                dscp_tag=self.config.dscp_tag
            )
            packets.append(pkt)
            pkt_id += 1
            current_time += self.interval

        return packets


class VideoTrafficGenerator:
    """
    Simulates real-time HD Video call traffic (e.g., WebRTC / H.264 / VP9).
    Characteristics:
    - Frame rate: 30 frames per second (every ~33.33ms).
    - Each video frame is sliced into a burst of 6 to 12 packets.
    - Packet sizes vary realistically between 800 and 1250 bytes.
    - Average bitrate: ~1.8 - 2.2 Mbps.
    - High sensitivity to jitter and packet loss (causes freezing and pixelation).
    """
    def __init__(self, config: FlowConfig, fps: int = 30, seed: int = 43):
        self.config = config
        self.frame_interval = 1.0 / fps   # ~0.0333 s
        self.random = random.Random(seed)

    def generate(self, start_id: int = 100000) -> List[Packet]:
        packets: List[Packet] = []
        current_time = self.config.start_time
        pkt_id = start_id

        while current_time <= self.config.end_time:
            # Each frame produces a burst of packets (I-frames or P-frames)
            # 1 in 30 is an I-frame (keyframe: larger burst)
            is_keyframe = (int(current_time / self.frame_interval) % 30 == 0)
            if is_keyframe:
                num_packets = self.random.randint(14, 18)
            else:
                num_packets = self.random.randint(6, 10)

            # Intra-burst packet spacing (packets sent rapidly across the frame period)
            burst_spacing = 0.0004  # 0.4ms apart within the frame
            for i in range(num_packets):
                size = int(self.random.gauss(1000, 100))
                size = max(500, min(1400, size))
                pkt_time = current_time + (i * burst_spacing)
                if pkt_time > self.config.end_time:
                    break
                pkt = Packet(
                    packet_id=pkt_id,
                    flow_id=self.config.flow_id,
                    traffic_type=self.config.traffic_type,
                    size_bytes=size,
                    created_at=pkt_time,
                    priority=self.config.priority,
                    dscp_tag=self.config.dscp_tag
                )
                packets.append(pkt)
                pkt_id += 1

            current_time += self.frame_interval

        return packets


class BulkTrafficGenerator:
    """
    Simulates high-volume background bulk data transfer (e.g., 4GB game update, file download).
    Characteristics:
    - Maximum Ethernet MTU size: 1500 bytes per packet.
    - Aggressive, continuous packet train arriving at the router trying to consume link capacity.
    - Offered load: ~14 - 16 Mbps (exceeding a 10 Mbps bottleneck link, creating severe congestion).
    - Latency tolerant, but greedy.
    """
    def __init__(self, config: FlowConfig, offered_rate_mbps: float = 14.0, seed: int = 44):
        self.config = config
        self.offered_rate_bps = offered_rate_mbps * 1_000_000
        self.packet_size = 1500
        # Average inter-packet interval = packet_size_bits / offered_rate_bps
        self.avg_interval = (self.packet_size * 8) / self.offered_rate_bps
        self.random = random.Random(seed)

    def generate(self, start_id: int = 500000) -> List[Packet]:
        packets: List[Packet] = []
        current_time = self.config.start_time
        pkt_id = start_id

        # Simulating bursty TCP window bursts
        while current_time <= self.config.end_time:
            # Burst of packets back-to-back followed by slight RTT pacing
            burst_size = self.random.randint(4, 12)
            for _ in range(burst_size):
                pkt = Packet(
                    packet_id=pkt_id,
                    flow_id=self.config.flow_id,
                    traffic_type=self.config.traffic_type,
                    size_bytes=self.packet_size,
                    created_at=current_time,
                    priority=self.config.priority,
                    dscp_tag=self.config.dscp_tag
                )
                packets.append(pkt)
                pkt_id += 1
                # Small intra-burst gap (wire transmission spacing at source)
                current_time += self.random.uniform(0.0001, 0.0003)
                if current_time > self.config.end_time:
                    break

            # Inter-burst pacing delay (TCP ACK clocking)
            current_time += self.random.expovariate(1.0 / (self.avg_interval * burst_size))

        return packets
