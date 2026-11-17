"""
Packet data structure and traffic definitions for the QoS Simulator.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TrafficType(str, Enum):
    VOICE = "VOICE"
    VIDEO = "VIDEO"
    BULK = "BULK"


class PriorityLevel(int, Enum):
    HIGH = 1   # Voice and Video (Time-sensitive, latency-critical)
    LOW = 2    # Bulk Data (Bandwidth-hungry, latency-tolerant)


@dataclass(slots=True)
class Packet:
    """
    Represents an individual network packet moving through the network.
    """
    packet_id: int
    flow_id: str
    traffic_type: TrafficType
    size_bytes: int
    created_at: float           # Simulation time when packet was generated (seconds)
    priority: PriorityLevel = PriorityLevel.LOW
    dscp_tag: str = "CS0"       # e.g. "EF" for voice, "AF41" for video, "CS0" for bulk
    
    # Lifecycle timestamps recorded by the simulation
    enqueued_at: Optional[float] = None
    service_started_at: Optional[float] = None
    delivered_at: Optional[float] = None
    dropped: bool = False
    drop_reason: Optional[str] = None

    @property
    def size_bits(self) -> int:
        return self.size_bytes * 8

    @property
    def queuing_delay(self) -> Optional[float]:
        if self.service_started_at is not None and self.enqueued_at is not None:
            return self.service_started_at - self.enqueued_at
        return None

    @property
    def end_to_end_latency(self) -> Optional[float]:
        if self.delivered_at is not None:
            return self.delivered_at - self.created_at
        return None
