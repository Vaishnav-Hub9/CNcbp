"""
High-Precision Discrete-Event Network Simulation Engine.
Models physical link transmission, queuing delays, buffer overflows, and propagation.
"""

import heapq
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional, Union, Dict, Any
from src.models.packet import Packet
from src.algorithms.fifo_queue import FIFOQueue
from src.algorithms.priority_queue import PriorityQueueScheduler
from src.metrics.collector import SimulationMetrics


class EventType(IntEnum):
    SAMPLE_METRICS = 0
    ARRIVAL = 1
    TOKEN_REFILL = 2
    DEPARTURE = 3


@dataclass(order=True)
class Event:
    time: float
    priority: int
    event_type: EventType = field(compare=False)
    data: Any = field(compare=False, default=None)


class DiscreteEventSimulator:
    """
    Simulates a bottleneck network link with queuing and transmission constraints.
    """
    def __init__(
        self,
        link_bandwidth_bps: float = 10_000_000.0,  # 10 Mbps
        propagation_delay_sec: float = 0.005,      # 5 ms
        queue_manager: Union[FIFOQueue, PriorityQueueScheduler] = None,
        run_name: str = "Simulation",
        total_time_sec: float = 30.0,
        sample_interval_sec: float = 0.05          # 50 ms
    ):
        self.link_bandwidth_bps = float(link_bandwidth_bps)
        self.propagation_delay = float(propagation_delay_sec)
        self.queue_manager = queue_manager
        self.run_name = run_name
        self.total_time = total_time_sec
        self.sample_interval = sample_interval_sec

        self.current_time: float = 0.0
        self.is_transmitting: bool = False
        self.current_packet: Optional[Packet] = None
        self.total_busy_time: float = 0.0
        self.last_busy_start: Optional[float] = None

        self.event_queue: List[Event] = []
        self.event_counter: int = 0
        self.has_pending_token_refill: bool = False
        self.metrics = SimulationMetrics(run_name, total_time_sec)

    def schedule_event(self, event_time: float, event_type: EventType, data: Any = None) -> None:
        self.event_counter += 1
        event = Event(time=event_time, priority=self.event_counter, event_type=event_type, data=data)
        heapq.heappush(self.event_queue, event)

    def load_packets(self, packets: List[Packet]) -> None:
        """
        Loads pre-generated packets into the event schedule.
        """
        for pkt in packets:
            self.metrics.get_flow_collector(pkt.flow_id, pkt.traffic_type).on_packet_generated(pkt)
            self.schedule_event(pkt.created_at, EventType.ARRIVAL, pkt)

    def run(self) -> SimulationMetrics:
        """
        Executes the discrete-event simulation until event queue is empty or total time reached.
        """
        # Schedule first metric sampling event
        self.schedule_event(0.0, EventType.SAMPLE_METRICS)

        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time

            if self.current_time > self.total_time + 1.0: # Allow 1s drain time after end
                break

            if event.event_type == EventType.SAMPLE_METRICS:
                self._handle_sample()
            elif event.event_type == EventType.ARRIVAL:
                self._handle_arrival(event.data)
            elif event.event_type == EventType.DEPARTURE:
                self._handle_departure()
            elif event.event_type == EventType.TOKEN_REFILL:
                self._handle_token_refill()

        return self.metrics

    def _handle_sample(self) -> None:
        """
        Records periodic queue length samples for plotting.
        """
        if isinstance(self.queue_manager, FIFOQueue):
            self.metrics.record_queue_sample(
                self.current_time, 
                total_packets=len(self.queue_manager.queue)
            )
        elif isinstance(self.queue_manager, PriorityQueueScheduler):
            self.metrics.record_queue_sample(
                self.current_time,
                total_packets=self.queue_manager.total_length,
                high_packets=len(self.queue_manager.high_queue),
                low_packets=len(self.queue_manager.low_queue)
            )

        if self.current_time + self.sample_interval <= self.total_time:
            self.schedule_event(self.current_time + self.sample_interval, EventType.SAMPLE_METRICS)

    def _handle_arrival(self, packet: Packet) -> None:
        """
        Handles arrival of a packet at the link interface.
        """
        flow_col = self.metrics.get_flow_collector(packet.flow_id, packet.traffic_type)

        if isinstance(self.queue_manager, FIFOQueue):
            enqueued = self.queue_manager.enqueue(packet, self.current_time)
        else:
            enqueued = self.queue_manager.enqueue(packet, self.current_time)

        if not enqueued:
            flow_col.on_packet_dropped(packet)
            return

        # If the link is idle, immediately start serving the queue
        if not self.is_transmitting:
            self._try_transmit_next()

    def _handle_departure(self) -> None:
        """
        Handles physical transmission completion of the current packet across the link.
        """
        if self.current_packet is not None:
            # End of transmission across the bottleneck link
            delivery_time = self.current_time + self.propagation_delay
            self.current_packet.delivered_at = delivery_time
            
            flow_col = self.metrics.get_flow_collector(
                self.current_packet.flow_id, 
                self.current_packet.traffic_type
            )
            flow_col.on_packet_delivered(self.current_packet)

            if self.last_busy_start is not None:
                self.total_busy_time += (self.current_time - self.last_busy_start)
                self.last_busy_start = None

            self.current_packet = None
            self.is_transmitting = False

        # Attempt to transmit the next packet in the queue
        self._try_transmit_next()

    def _handle_token_refill(self) -> None:
        """
        Fires when tokens are expected to be available for a shaped packet.
        """
        self.has_pending_token_refill = False
        if not self.is_transmitting:
            self._try_transmit_next()

    def _try_transmit_next(self) -> None:
        """
        Pulls the next eligible packet from the queue and begins transmission.
        """
        if self.is_transmitting:
            return

        if isinstance(self.queue_manager, FIFOQueue):
            pkt = self.queue_manager.dequeue()
        else:
            pkt = self.queue_manager.dequeue(self.current_time)

        if pkt is not None:
            # Begin transmission of this packet
            self.is_transmitting = True
            self.current_packet = pkt
            pkt.service_started_at = self.current_time
            self.last_busy_start = self.current_time

            # Transmission time = bits / bandwidth
            tx_duration = pkt.size_bits / self.link_bandwidth_bps
            self.schedule_event(self.current_time + tx_duration, EventType.DEPARTURE)
        else:
            # No packet ready right now.
            # If using PriorityQueue with TokenBucket, check if a low packet is waiting for tokens.
            if isinstance(self.queue_manager, PriorityQueueScheduler):
                wait_time = self.queue_manager.time_until_token_ready(self.current_time)
                if wait_time is not None and wait_time > 0 and not self.has_pending_token_refill:
                    self.has_pending_token_refill = True
                    self.schedule_event(self.current_time + wait_time, EventType.TOKEN_REFILL)
