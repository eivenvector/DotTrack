from matplotlib.patches import Circle

class TrackableDot(Circle):
    def __init__(self, center, radius, color, velocity, idnum):
        super(TrackableDot, self).__init__(center, radius, color=color)
        self.velocity = velocity
        self.colliding = 0
        self.id = idnum

    def update_position(self, dt):
        """Updates the position of the TrackableDot using the velocity and
        dt as the time scale.
        Args:
            dt: time interval
        """
        self.center = self.center[0] + self.velocity[0] * dt, self.center[1] + self.velocity[1] * dt
