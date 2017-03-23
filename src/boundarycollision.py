class BoundaryCollisionDetector:
    def __init__(self, boundary):
        self.boundary = boundary

    def detect_collision(self, entity):
        """Uses the boundary to detect a collision.
        Args:
            entity: An object contained in the boundary which can collide with
            boundary.
        Returns:
            collision_type: An integer which represents the collision type:
                1: left
                4: bottom
                1: right
                4: top
        """
        top_collision = (self.boundary.HEIGHT - entity.center[1] <= entity.radius)
        bottom_collision = (entity.center[1] <= entity.radius)
        left_collision = (entity.center[0] <= entity.radius)
        right_collision = (self.boundary.WIDTH - entity.center[0] <= entity.radius)
        collision_type = 0
        collision_type += 4 * top_collision + 4 * bottom_collision + \
                            1 * left_collision + 1 * right_collision
        return collision_type

    def update_velocity(self, entity):
        """Updates velocity after a collision between a boundary and an entity
        is detected. This is an elastic collision.
        Args:
            entity: The object whose velocity will be updated.
        """
        collision_type = detect_collision(entity)
        if (collision_type > 0):
            if (collision_type == 4):
                ## This is a top or bottom collision
                entity.velocity[1] *= -1
            else if(collision_type == 1):
                ## This is a left or right collision
                entity.velocity[0] *= -1
            else if (collision_type > 4):
                ## This is multiple collision occuring
                entity.velocity[0] *= -1
                entity.velocity[1] *= -1
        else:
            return
