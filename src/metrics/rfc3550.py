"""
RFC 3550 Real-Time Transport Protocol (RTP) Interarrival Jitter Calculation.
Defines the standard algorithm used by VoIP and video conferencing systems to measure jitter.
"""

from typing import List, Tuple, Optional


class RFC3550JitterCalculator:
    """
    Computes interarrival jitter according to RFC 3550 Section 6.4.1.
    Formula:
      D(i, j) = (R_j - S_j) - (R_i - S_i)
      J = J + (|D(i, j)| - J) / 16
    where:
      S_k = packet k generation / transmission timestamp at source
      R_k = packet k arrival / delivery timestamp at receiver
    """
    def __init__(self):
        self.jitter: float = 0.0
        self.prev_send_time: Optional[float] = None
        self.prev_recv_time: Optional[float] = None
        self.sample_count: int = 0
        self.history: List[Tuple[float, float]] = []  # (recv_time, current_jitter)

    def record_packet(self, send_time: float, recv_time: float) -> float:
        """
        Processes a newly delivered packet and updates the running jitter estimate.
        Returns the updated jitter value in seconds.
        """
        if self.prev_send_time is not None and self.prev_recv_time is not None:
            # Transit time difference between consecutive packets
            transit_prev = self.prev_recv_time - self.prev_send_time
            transit_curr = recv_time - send_time
            d = abs(transit_curr - transit_prev)
            
            # RFC 3550 exponential filter with gain 1/16
            self.jitter += (d - self.jitter) / 16.0
            self.sample_count += 1
            self.history.append((recv_time, self.jitter))

        self.prev_send_time = send_time
        self.prev_recv_time = recv_time
        return self.jitter

    @property
    def current_jitter_ms(self) -> float:
        return self.jitter * 1000.0

    def reset(self) -> None:
        self.jitter = 0.0
        self.prev_send_time = None
        self.prev_recv_time = None
        self.sample_count = 0
        self.history.clear()
