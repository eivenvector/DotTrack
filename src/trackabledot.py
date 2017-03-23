from matplotlib.patches import Circle

class TrackableDot(Circle):
    __init__(self, radius, center, color, velocity)
        super(TrackableDot, self)._init__(location, radius, color=color))
        self.velocity = velocity

    def update_position(self, dt):
        """Updates the position of the TrackableDot using the velocity and
        dt as the time scale.
        Args:
            dt: time interval
        """
        self.center = self.center[0] + self.velocity[0] * dt, \
                      self.center[1] + self.velocity[1]
