import bpy
import math
import random
from mathutils import Vector

# The number of generated particles is not exact due to random particle location selection
# If the number of the expected generated dust particle (num_particles) is 5000 and the expected number of gas particles is 25000 (5 * 5000)
# So the expected sum of all particles is 30000
# But, in fact, the generated number of the particles will be about 15000 instead of 30000
# Therefore the num_particles should be expected_number_of_dust_particles * 2 to receive the +/- correct result

# Get the comet and sun objects
comet_obj = bpy.data.objects["Comet_67P"]
sun_location = Vector((0, -500, 0))  # Position of the Sun
comet_center = comet_obj.location

# Determine the direction from the comet center to the Sun
light_direction = (sun_location - comet_center).normalized()

# Check if the vertex is on the daylight side of the comet
def is_day_side(vertex):
    vertex_global = comet_obj.matrix_world @ vertex.co
    vertex_to_center = vertex_global - comet_center
    return vertex_to_center.dot(light_direction) > 0

def generate_particle(vertex, index):
    x, y, z = comet_obj.matrix_world @ vertex.co  # Get the global coordinates of the vertex

    # Offset the particle relative to the vertex
    phi = random.uniform(0, 2 * math.pi)
    theta = random.uniform(0, math.pi)
    r = random.uniform(0, distance_from_surface)

    x += r * math.sin(phi) * math.cos(theta)
    y += r * math.sin(phi) * math.sin(theta)
    z += r * math.cos(phi)

    # Create a unique name for each particle
    particle_name = f"Particle{index:05d}"
    # Create a new object for the particle and link it to the mesh
    particle_obj = bpy.data.objects.new(particle_name, particle_mesh)
    # Add the particle object to the scene
    bpy.context.collection.objects.link(particle_obj)
    # Set the particle's location
    particle_obj.location = (x, y, z)
    # Set the particle's scale
    particle_obj.scale = (particle_radius, particle_radius, particle_radius)
    # Create a material for the particle and set its color
    particle_obj.active_material = bpy.data.materials.new(name="ParticleMaterial")
    particle_obj.active_material.diffuse_color = particle_color

def generate_gas_particle(vertex, index):
    x, y, z = comet_obj.matrix_world @ vertex.co  # Get the global coordinates of the vertex

    # Offset the particle relative to the vertex
    phi = random.uniform(0, 2 * math.pi)
    theta = random.uniform(0, math.pi)
    r = random.uniform(0, distance_from_surface)

    x += r * math.sin(phi) * math.cos(theta)
    y += r * math.sin(phi) * math.sin(theta)
    z += r * math.cos(phi)

    # Create a unique name for each gas particle
    gas_particle_name = f"GasParticle{index:05d}"
    # Create a new object for the gas particle and link it to the mesh
    gas_particle_obj = bpy.data.objects.new(gas_particle_name, gas_particle_mesh)
    # Add the gas particle object to the scene
    bpy.context.collection.objects.link(gas_particle_obj)
    # Set the gas particle's location
    gas_particle_obj.location = (x, y, z)
    # Set the gas particle's scale
    gas_particle_obj.scale = (particle_radius, particle_radius, particle_radius)
    # Create a material for the gas particle and set its color
    gas_particle_obj.active_material = bpy.data.materials.new(name="GasParticleMaterial")
    gas_particle_obj.active_material.diffuse_color = gas_particle_color

# Create dust particles
num_particles = 20000 # the number is set according to the GPU opportunities because the real number is too big
particle_radius = 0.000805112 # 0.0001 km
distance_from_surface = 1.558300175 # 0.2 km - the number is set according to GPU opportunities
particle_color = (0, 1, 0, 1)  # Green color

# Create a new mesh for dust particles
particle_mesh = bpy.data.meshes.new("ParticleMesh")

# Generate dust particles within a specified distance from the comet surface
for i in range(num_particles):
    # Select a random vertex on the comet
    random_vertex_index = random.randint(0, len(comet_obj.data.vertices) - 1)
    vertex = comet_obj.data.vertices[random_vertex_index]

    # Check if the vertex is on the daylight side
    if is_day_side(vertex):
        # Generate 95% of particles on the daylight side
        if random.random() < 0.95:
            # Generate a particle
            generate_particle(vertex, i)
    else:
        # Generate 5% of particles on the nighttime side
        if random.random() < 0.05:
            # Generate a particle
            generate_particle(vertex, i)

# Create gas particles
num_gas_particles = 5 * num_particles
gas_particle_color = (0, 0, 1, 1)  # Blue color

# Create a new mesh for gas particles
gas_particle_mesh = bpy.data.meshes.new("GasParticleMesh")

# Generate gas particles within a specified distance from the comet surface
for i in range(num_gas_particles):
    # Select a random vertex on the comet
    random_vertex_index = random.randint(0, len(comet_obj.data.vertices) - 1)
    vertex = comet_obj.data.vertices[random_vertex_index]

    # Check if the vertex is on the daylight side
    if is_day_side(vertex):
        # Generate 95% of particles on the daylight side
        if random.random() < 0.95:
            # Generate a gas particle
            generate_gas_particle(vertex, i)
    else:
        # Generate 5% of particles on the nighttime side
        if random.random() < 0.05:
            # Generate a gas particle
            generate_gas_particle(vertex, i)
