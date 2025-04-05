import utime


class PID:
    def __init__(self, kp, ki, kd, setpoint=0, sample_time=100, output_limits=(None, None)):
        """
        Initialize the PID controller.

        Args:
            kp (float): Proportional gain.
            ki (float): Integral gain.
            kd (float): Derivative gain.
            setpoint (float): The desired target value.
            sample_time (int): Time between updates in milliseconds.
            output_limits (tuple): Tuple of (min, max) limits for the PID output.
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.sample_time = sample_time  # in milliseconds

        self.min_output, self.max_output = output_limits

        self.last_time = utime.ticks_ms()
        self.last_error = 0
        self.integral = 0

    def update(self, measured_value):
        """
        Update the PID controller with the measured value and calculate the output.

        Args:
            measured_value (float): The current value from the sensor.

        Returns:
            float or None: The PID output. Returns None if the sample time has not elapsed.
        """
        now = utime.ticks_ms()
        dt = utime.ticks_diff(now, self.last_time)

        if dt >= self.sample_time:
            error = self.setpoint - measured_value
            self.integral += error * dt
            # Compute derivative (avoid division by zero)
            derivative = (error - self.last_error) / dt if dt > 0 else 0

            output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)

            # Clamp output to the limits if they are set
            if self.max_output is not None and output > self.max_output:
                output = self.max_output
            elif self.min_output is not None and output < self.min_output:
                output = self.min_output

            self.last_error = error
            self.last_time = now

            return output
        else:
            return None
