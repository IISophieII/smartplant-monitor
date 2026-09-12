"""Deterministic, synthetic motor telemetry; no physical fault model claimed."""
import random

FIELDS = ("temperature", "vibration", "rpm", "current")


class Simulator:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.mode = "normal"
        self.progress = 0.0

    def set_mode(self, mode):
        if mode not in ("normal", "progressive_fault"):
            raise ValueError("Unsupported simulation mode")
        self.mode = mode
        self.progress = 0.0

    def sample(self):
        if self.mode == "progressive_fault":
            self.progress = min(1.0, self.progress + 1 / 60)
        p = self.progress
        return dict(zip(FIELDS, [
            round(self.rng.gauss(48 + 32*p, 0.8), 2),
            round(max(0, self.rng.gauss(1.3 + 6*p, 0.08)), 2),
            round(self.rng.gauss(1450 - 180*p, 7), 2),
            round(self.rng.gauss(3.8 + 3*p, 0.1), 2),
        ]))
