"""
Simulates instrumentation readings from an energy system
(e.g. EV battery pack / charging station / industrial load).

Generates a stream of readings with occasional injected anomalies
so the agent has something real to reason about.
"""

import random
import math

def generate_reading(t: int, inject_anomaly_prob: float = 0.15):
    """
    Returns one instrumentation reading at time-step t.
    t: integer time step (e.g. minutes)
    """
    # baseline healthy battery behavior
    base_voltage = 48 + 2 * math.sin(t / 20)          # volts, slow oscillation
    base_current = 10 + 3 * math.sin(t / 10)           # amps
    base_temp = 30 + 5 * math.sin(t / 30)               # celsius
    soc = max(0, min(100, 80 - 0.05 * t + random.uniform(-1, 1)))  # slow discharge

    voltage = base_voltage + random.uniform(-0.5, 0.5)
    current = base_current + random.uniform(-0.5, 0.5)
    temperature = base_temp + random.uniform(-1, 1)

    anomaly_injected = False
    if random.random() < inject_anomaly_prob:
        anomaly_injected = True
        anomaly_type = random.choice(["overheat", "voltage_drop", "current_spike", "fast_discharge"])
        if anomaly_type == "overheat":
            temperature += random.uniform(15, 25)
        elif anomaly_type == "voltage_drop":
            voltage -= random.uniform(5, 10)
        elif anomaly_type == "current_spike":
            current += random.uniform(15, 25)
        elif anomaly_type == "fast_discharge":
            soc -= random.uniform(10, 20)

    return {
        "t": t,
        "voltage": round(voltage, 2),
        "current": round(current, 2),
        "temperature": round(temperature, 2),
        "soc": round(max(0, min(100, soc)), 2),
        "anomaly_injected": anomaly_injected,
    }


def generate_stream(n_steps: int = 30, inject_anomaly_prob: float = 0.15):
    return [generate_reading(t, inject_anomaly_prob) for t in range(n_steps)]


if __name__ == "__main__":
    # quick manual test
    for r in generate_stream(10):
        print(r)