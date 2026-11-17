"""
Priority Queue Scheduler with Token Bucket Traffic Shaping.
Implements Quality of Service (QoS) differentiation:
- High-Priority Queue: Latency-sensitive traffic (Voice & Video)
- Low-Priority Queue: Delay-tolerant traffic (Bulk download) shaped by Token Bucket.
"""

from collections import deque
from typing import Optional, List, Tuple
from src.models.packet import Packet, PriorityLevel
from src.algorithms.token_bucket import TokenBucketShaper


class PriorityQueueScheduler:
    """
    Two-tier Strict Priority Scheduler.
    High-priority queue is always served first.
    Low-priority traffic is rate-limited by a token bucket shaper to prevent starvation.
    """
    def __init__(
        self, 
        high_max_packets: int = 100, 
        low_max_packets: int = 100,
        shaper: Optional[TokenBucketShaper] = None
    ):
        self.high_queue: deque[Packet] = deque()
        self.low_queue: deque[Packet] = deque()
        self.high_max_packets = high_max_packets
        self.low_max_packets = low_max_packets
        self.shaper = shaper

        self.high_bytes: int = 0
        self.low_bytes: int = 0

        # Statistics
        self.total_enqueued_high: int = 0
        self.total_enqueued_low: int = 0
        self.total_dropped_high: int = 0
        self.total_dropped_low: int = 0
        self.dropped_packets: List[Packet] = []

    def enqueue(self, packet: Packet, current_time: float) -> bool:
        """
        Routes packet into the appropriate queue based on priority level.
        Returns True if enqueued, False if dropped.
        """
        packet.enqueued_at = current_time

        if packet.priority == PriorityLevel.HIGH:
            if len(self.high_queue) >= self.high_max_packets:
                packet.dropped = True
                packet.drop_reason = "High-Priority Queue Overflow"
                self.total_dropped_high += 1
                self.dropped_packets.append(packet)
                return False
            self.high_queue.append(packet)
            self.high_bytes += packet.size_bytes
            self.total_enqueued_high += 1
            return True
        else:
            if len(self.low_queue) >= self.low_max_packets:
                packet.dropped = True
                packet.drop_reason = "Low-Priority Queue Overflow"
                self.total_dropped_low += 1
                self.dropped_packets.append(packet)
                return False
            self.low_queue.append(packet)
            self.low_bytes += packet.size_bytes
            self.total_enqueued_low += 1
            return True

    def dequeue(self, current_time: float) -> Optional[Packet]:
        """
        Dequeues the next packet according to strict priority logic.
        High-priority queue is ALWAYS drained first.
        Low-priority queue is shaped by the token bucket if configured.
        """
        # 1. Drain High Priority Queue first
        if self.high_queue:
            pkt = self.high_queue.popleft()
            self.high_bytes -= pkt.size_bytes
            return pkt

        # 2. Check Low Priority Queue
        if self.low_queue:
            candidate = self.low_queue[0]
            if self.shaper is not None:
                if self.shaper.can_send(candidate.size_bytes, current_time):
                    self.shaper.consume(candidate.size_bytes, current_time)
                    pkt = self.low_queue.popleft()
                    self.low_bytes -= pkt.size_bytes
                    return pkt
                else:
                    # Low-priority packet must wait for tokens to refill
                    return None
            else:
                pkt = self.low_queue.popleft()
                self.low_bytes -= pkt.size_bytes
                return pkt

        return None

    def time_until_token_ready(self, current_time: float) -> Optional[float]:
        """
        If high-priority queue is empty and low-priority head is waiting for tokens,
        returns seconds until sufficient tokens are refilled.
        """
        if self.high_queue or not self.low_queue or self.shaper is None:
            return None
        candidate = self.low_queue[0]
        return self.shaper.time_until_tokens(candidate.size_bytes, current_time)

    @property
    def is_empty(self) -> bool:
        return len(self.high_queue) == 0 and len(self.low_queue) == 0

    @property
    def total_length(self) -> int:
        return len(self.high_queue) + len(self.low_queue)
