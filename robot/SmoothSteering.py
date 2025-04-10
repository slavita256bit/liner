import time
import math

class SmoothSteering:
    def __init__(self):
        # Current state variables (in degrees or whatever unit your system uses)
        self.current_angle = 0          # The last computed angle.
        self.start_angle = 0            # Angle at the moment when transition started.
        self.target_angle = 0           # Desired target angle.
        self.transition_duration = 1000 # Duration of the transition in ms.
        self.start_time = time.ticks_ms()

        # Select the default easing profile
        self.profile_name = "linear"

        # Map available easing profiles to their functions.
        self.profiles = {
            "linear": self.linear,
            "ease-in": self.ease_in,
            "ease-out": self.ease_out,
            "ease-in-out": self.ease_in_out,
            "exp": self.exp_profile,
        }

    def set_profile(self, profile_name):
        """
        Change the acceleration/easing profile.
        Raises ValueError if profile not recognized.
        """
        if profile_name in self.profiles:
            self.profile_name = profile_name
        else:
            raise ValueError("Profile '{}' not recognized.".format(profile_name))

    def update_target(self, new_target, duration_ms=1000):
        """
        Update the target angle and the transition duration.
        If a new target is given during an ongoing transition, we use the
        current interpolated angle as the new starting point.

        Args:
            new_target: The new desired steering angle.
            duration_ms: The duration (in milliseconds) over which to transition.
        """
        # Recompute current angle from previous transition so that
        # we start from the current position.
        self.current_angle = self.get_current_angle()
        self.start_angle = self.current_angle
        self.target_angle = new_target
        self.transition_duration = duration_ms
        self.start_time = time.ticks_ms()

    def get_current_angle(self):
        """
        Compute and return the current angle based on the elapsed time
        and selected easing profile.
        """
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, self.start_time)
        # Clamp progress in the range 0 to 1.
        progress = max(0, min(elapsed / self.transition_duration, 1))
        # Get the profile function.
        easing = self.profiles.get(self.profile_name, self.linear)
        factor = easing(progress)
        # Interpolate between start_angle and target_angle.
        angle = self.start_angle + (self.target_angle - self.start_angle) * factor
        return angle

    # Easing functions:
    def linear(self, t):
        """Linear interpolation: f(t) = t"""
        return t

    def ease_in(self, t):
        """Ease-in: accelerate from zero velocity. f(t) = t^2"""
        return t * t

    def ease_out(self, t):
        """Ease-out: decelerate to zero velocity. f(t) = 1 - (1-t)^2"""
        return 1 - (1 - t) * (1 - t)

    def ease_in_out(self, t):
        """
        Ease-in-out: acceleration until halfway, then deceleration.
        This is a simple formulation.
        """
        if t < 0.5:
            return 2 * t * t
        else:
            return -2 * t * t + 4 * t - 1

    def exp_profile(self, t):
        """
        Exponential easing: creates a sharp acceleration
        at the beginning that levels off. Adjust the exponent base as needed.
        f(t) = (exp(t) - 1) / (e - 1)
        """
        return (math.exp(t) - 1) / (math.e - 1)
