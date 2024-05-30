import bpy
import math
import random
from mathutils import Vector

# Get the comet and sun objects
comet_obj = bpy.data.objects["Comet_67P"]
sun_location = Vector((0, -500, 0))  # Sun position
comet_center = comet_obj.location

# Determine the direction from the comet center to the Sun
light_direction = (sun_location - comet_center).normalized()

# Determine the speeds of particles
gas_particle_speed = 4.347607239
min_particle_speed = 80.51124517
max_particle_speed = 322.0449807

# Animate particle movement
for obj in bpy.context.scene.objects:
    if obj.name.startswith("Particle") or obj.name.startswith("GasParticle"):
        # Determine the particle speed
        if obj.name.startswith("Particle"):
            particle_speed = random.uniform(min_particle_speed, max_particle_speed)
        else:
            particle_speed = gas_particle_speed

        # Get the initial position of the particle
        start_position = obj.location

        # Calculate the movement direction (opposite to the Sun)
        direction = -light_direction

        # Calculate the final position of the particle
        end_position = start_position + direction * particle_speed

        # Add keyframes for animation
        obj.location = start_position
        obj.keyframe_insert(data_path="location", frame=1)
        obj.location = end_position
        obj.keyframe_insert(data_path="location", frame=500)  # Set the desired animation duration
