class KalmanFilter1D:
    def __init__(self, process_noise=1e-5, measurement_noise=1e-2, estimate_error=1.0, initial_estimate=0.0):
        self.Q = process_noise        # Process noise covariance
        self.R = measurement_noise    # Measurement noise covariance
        self.P = estimate_error       # Estimation error covariance
        self.x = initial_estimate     # Initial state estimate

    def update(self, measurement):
        # Prediction update
        self.P += self.Q

        # Measurement update
        K = self.P / (self.P + self.R)
        self.x += K * (measurement - self.x)
        self.P *= (1 - K)

        return self.x

    def set_measurement_noise(self, noise):
        self.R = noise

    def set_process_noise(self, noise):
        self.Q = noise

    def reset(self, estimate=0.0, error=1.0):
        self.x = estimate
        self.P = error


class MovingAverage:
    def __init__(self, size=5):
        self.size = size
        self.buffer = []

    def update(self, value):
        self.buffer.append(value)
        if len(self.buffer) > self.size:
            self.buffer.pop(0)
        return sum(self.buffer) / len(self.buffer)


class ExponentialSmoothing:
    def __init__(self, alpha=0.2, initial_value=0.0):
        self.alpha = alpha
        self.ema = initial_value

    def update(self, value):
        self.ema = self.alpha * value + (1 - self.alpha) * self.ema
        return self.ema
