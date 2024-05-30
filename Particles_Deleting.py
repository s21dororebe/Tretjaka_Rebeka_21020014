import bpy

# Get all objects in the scene
all_objects = bpy.context.scene.objects

# Iterate through each object
for obj in all_objects:
    # Check if the object name starts with "Particle" or "GasParticle"
    if obj.name.startswith("Particle") or obj.name.startswith("GasParticle"):
        # Remove the object
        bpy.data.objects.remove(obj, do_unlink=True)
