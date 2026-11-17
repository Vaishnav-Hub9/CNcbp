"""
Token Bucket Traffic Shaper.
Enforces an average sustained transmission rate while allowing controlled bursts.
"""

from typing import Optional


class TokenBucketShaper:
    """
    Token Bucket rate limiter for traffic shaping.
    Tokens represent allowed byte transmissions.
    """
    def __init__(self, rate_bps: float, capacity_bytes: int, initial_bytes: Optional[int] = None):
        self.rate_bps = float(rate_bps)
        self.rate_bytes_per_sec = self.rate_bps / 8.0
        self.capacity_bytes = float(capacity_bytes)
        self.tokens_bytes = float(initial_bytes if initial_bytes is not None else capacity_bytes)
        self.last_update_time: float = 0.0

    def update(self, current_time: float) -> None:
        """
        Refills tokens according to elapsed simulation time.
        """
        if current_time > self.last_update_time:
            elapsed = current_time - self.last_update_time
            new_tokens = elapsed * self.rate_bytes_per_sec
            self.tokens_bytes = min(self.capacity_bytes, self.tokens_bytes + new_tokens)
            self.last_update_time = current_time

    def can_send(self, packet_size_bytes: int, current_time: float) -> bool:
        """
        Checks whether the bucket has enough tokens to transmit the packet at current_time.
        Includes a micro-epsilon tolerance for floating-point precision.
        """
        self.update(current_time)
        return (self.tokens_bytes + 1e-5) >= packet_size_bytes

    def consume(self, packet_size_bytes: int, current_time: float) -> bool:
        """
        Attempts to consume tokens for transmission. Returns True if successful.
        """
        self.update(current_time)
        if (self.tokens_bytes + 1e-5) >= packet_size_bytes:
            self.tokens_bytes = max(0.0, self.tokens_bytes - packet_size_bytes)
            return True
        return False

    def time_until_tokens(self, needed_bytes: int, current_time: float) -> float:
        """
        Calculates time in seconds until the bucket will have accumulated needed_bytes.
        Adds a safety buffer (1 microsecond) to prevent zero-delta floating point event thrashing.
        """
        self.update(current_time)
        if (self.tokens_bytes + 1e-5) >= needed_bytes:
            return 0.0
        deficit = needed_bytes - self.tokens_bytes
        time_needed = deficit / self.rate_bytes_per_sec
        return max(1e-5, time_needed + 1e-6)
