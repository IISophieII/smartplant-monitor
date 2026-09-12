import numpy as np
from sklearn.ensemble import IsolationForest

from .simulator import FIELDS, Simulator


class Detector:
    def __init__(self):
        sim = Simulator(seed=2026)
        samples = [sim.sample() for _ in range(1500)]
        training = [[sample[key] for key in FIELDS] for sample in samples]
        self.model = IsolationForest(n_estimators=100, contamination=0.02, random_state=42, n_jobs=1)
        self.model.fit(training)

    def evaluate(self, values):
        margin = float(self.model.decision_function([[values[k] for k in FIELDS]])[0])
        reasons = []
        for key, threshold, label in [("temperature", 65, "温度超过演示阈值 65°C"),
                                      ("vibration", 4.5, "振动超过演示阈值 4.5 mm/s"),
                                      ("current", 5.5, "电流超过演示阈值 5.5 A")]:
            if values[key] > threshold:
                reasons.append(label)
        risk = float(np.clip(-margin / 0.25, 0, 1))
        if reasons:
            risk = max(risk, 0.75)
        status = "critical" if reasons else "warning" if margin < 0 else "normal"
        return {"anomaly_margin": round(margin, 4), "health": round(100*(1-risk)),
                "status": status, "reasons": reasons or (["偏离合成正常基线"] if margin < 0 else [])}
