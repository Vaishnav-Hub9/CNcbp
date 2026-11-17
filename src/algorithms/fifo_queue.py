"""
First-In, First-Out (FIFO) Best-Effort Queue with Tail-Drop.
Represents default, unmanaged network link queuing behavior.
"""

from collections import deque
from typing import Optional, List
from src.models.packet import Packet


class FIFOQueue:
    """
    Standard single-queue FIFO buffer.
    All packets are treated equally regardless of traffic type or urgency.
    """
    def __init__(self, max_packets: int = 100, max_bytes: Optional[int] = None):
        self.max_packets = max_packets
        self.max_bytes = max_bytes
        self.queue: deque[Packet] = deque()
        self.current_bytes: int = 0
        
        # Statistics
        self.total_enqueued: int = 0
        self.total_dropped: int = 0
        self.dropped_packets: List[Packet] = []

    def enqueue(self, packet: Packet, current_time: float) -> bool:
        """
        Attempts to enqueue a packet.
        Returns True if enqueued, False if dropped due to buffer overflow.
        """
        # Check capacity
        is_packet_limit_reached = len(self.queue) >= self.max_packets
        is_byte_limit_reached = (
            self.max_bytes is not None and 
            (self.current_bytes + packet.size_bytes) > self.max_bytes
        )

        if is_packet_limit_reached or is_byte_limit_reached:
            packet.dropped = True
            packet.drop_reason = "FIFO Buffer Overflow (Tail Drop)"
            self.total_dropped += 1
            self.dropped_packets.append(packet)
            return False

        packet.enqueued_at = current_time
        self.queue.append(packet)
        self.current_bytes += packet.size_bytes
        self.total_enqueued += 1
        return True

    def dequeue(self) -> Optional[Packet]:
        """
        Dequeues and returns the packet at the head of the queue.
        """
        if not self.queue:
            return None
        packet = self.queue.popleft()
        self.current_bytes -= packet.size_bytes
        return packet

    def peek(self) -> Optional[Packet]:
        """
        Inspects the next packet without dequeuing.
        """
        return self.queue[0] if self.queue else None

    @property
    def is_empty(self) -> bool:
        return len(self.queue) == 0

    @property
    def length(self) -> int:
        return len(self.queue)
