from mathutils import Vector, noise
import bpy
import json
import logging

#This class is responsible for generating nucleus objects. It has methods for creating and merging cores from Blender objects and cleaning up the project after the process.
class NucleusGenerator:
    """
    Class responsible for generating nucleus objects out of multiple cores, merging them and modifying them to make them look like a comet
    """

    def __init__(self):
        self.core_generators = {}

    def create_and_merge_cores_from_objects(self, core_objects, core_data):
        """
        Create and merge cores based on Blender objects.

        This function takes a dictionary of Blender objects representing the cores,
        performs transformations on the cores, merges the cores together, and returns
        a dictionary of the created core objects.

        :param core_objects: Dictionary containing Blender objects representing the cores.
        :type core_objects: dict
        :return: Dictionary containing the core objects with their names as keys.
        :rtype: dict
        """

        cores = {}

        # Perform operations on core objects
        for core_name, core_object in core_objects.items():
            try:
                core = core_object

                # Apply necessary transformations
                remesh = Nucleus_modulator.mod_remesh_sharp(core, core_data[core_name]["remesh"])
                Nucleus_modulator.apply_modifier(remesh)

                noise_vertices = Nucleus_modulator.noise_vertices(core, core_data[core_name]["noise_vertices_2"])

                if "noise_displace_rough" in core_data[core_name]:
                    noise_displace_rough_data = core_data[core_name]["noise_displace_rough"]
                    noise_displace_rough = Nucleus_modulator.mod_noise_displace(core, noise_displace_rough_data["strength"], noise_displace_rough_data["size"])
                    Nucleus_modulator.apply_modifier(noise_displace_rough)

                if "noise_displace_fine" in core_data[core_name]:
                    noise_displace_fine_data = core_data[core_name]["noise_displace_fine"]
                    noise_displace_fine = Nucleus_modulator.mod_noise_displace(core, noise_displace_fine_data["strength"], noise_displace_fine_data["size"])
                    Nucleus_modulator.apply_modifier(noise_displace_fine)

                subdivision = Nucleus_modulator.mod_add_subdivision(core, core_data[core_name]["subdiv2"], core_data[core_name]["subdiv2"])
                Nucleus_modulator.apply_modifier(subdivision)
                Nucleus_modulator.set_smooth(True)

                TextureHandler.material_link("AsteroidSurface.001", core)
                TextureHandler.material_displacement("AsteroidSurface.001", 2.4)

                cores[core_name] = core
            except Exception as e:
                logging.error(f"Error creating core: {core_name} - {e}")

        # Merge cores
        for merge_data in core_data['merge']:
            core_name = merge_data['core']
            addon_names = list(merge_data.keys())
            addon_names.remove('core')

            if core_name in cores and all(addon_name in cores for addon_name in addon_names):
                core = cores[core_name]
                addons = [cores[addon_name] for addon_name in addon_names]
                self.core_merger(core, addons)
                for addon in addons:
                    self.object_cleaner(addon)
            else:
                logging.error(f"The merging of {core_name} and {addon_names} failed. Either one or neither of them have not been created. Check the nucleus.json to make sure all merge objects exist")

        # Clean up project
        self.project_cleaner()

        # Filter out addons
        cores = {name: core for name, core in cores.items() if "addon" not in name}

        return cores

    def core_merger(self, core, addons):
        """
        Merges the core with an according addon
        :param core: the object the addon shall be added to
        :type core: bpy.types.object
        :param addon: the object which is added to the core
        :type addon: bpy.types.object
        """
        core.select_set(True)
        bpy.context.view_layer.objects.active = core

        for addon in addons:
            bpy.ops.object.modifier_add(type='BOOLEAN')
            boolean_modifier = bpy.context.object.modifiers[-1]
            boolean_modifier.operation = 'UNION'
            boolean_modifier.solver = 'FAST'
            boolean_modifier.object = addon
            bpy.ops.object.modifier_apply(modifier="Boolean", report=True)

    def object_cleaner(self, removable_object):
        logging.info(f"Cleaning objects...")
        if removable_object is not None:
            bpy.data.objects.remove(removable_object, do_unlink=True)

        for mesh in bpy.data.meshes:
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)

    def project_cleaner(self):
        for collection in bpy.data.collections:
            if collection.name != "Collection":
                bpy.data.collections.remove(collection)

# This class contains static methods for applying various modifiers to the core objects, such as remeshing, noise displacement, adding subdivision, and smoothing.
class Nucleus_modulator:

    @staticmethod
    def mod_remesh_sharp(object, remesh_data):
        bpy.ops.object.modifier_add(type='REMESH')
        modifier = bpy.context.object.modifiers[-1]
        modifier.mode = 'SHARP'
        modifier.octree_depth = remesh_data["octree_depth"]
        modifier.scale = remesh_data["scale"]
        modifier.use_remove_disconnected = False
        return modifier

    @staticmethod
    def mod_noise_displace(object, strength, size):
        bpy.ops.object.modifier_add(type='DISPLACE')
        modifier = bpy.context.object.modifiers[-1]
        modifier.strength = strength
        texture = bpy.data.textures.new('DisplacementTexture', 'CLOUDS')
        texture.noise_scale = size
        modifier.texture = texture
        modifier.texture_coords = 'OBJECT'
        modifier.direction = 'RGB_TO_XYZ'
        return modifier

    @staticmethod
    def mod_add_subdivision(object, levels_viewport, levels_render):
        bpy.ops.object.modifier_add(type='SUBSURF')
        modifier = bpy.context.object.modifiers[-1]
        modifier.levels = levels_viewport
        modifier.render_levels = levels_render
        return modifier

    @staticmethod
    def apply_modifier(modifier):
        bpy.ops.object.modifier_apply(modifier=modifier.name)

    @staticmethod
    def set_smooth(smooth):
        bpy.ops.object.shade_smooth() if smooth else bpy.ops.object.shade_flat()

    @staticmethod
    def noise_vertices(object, noise_data):
        for v in object.data.vertices:
            noise_scale = noise_data["noise_scale"]
            v.co += noise.noise(Vector((v.co.x, v.co.y, v.co.z))) * noise_scale

    @staticmethod
    def noise_edges(object, noise_data):
        for edge in object.data.edges:
            for v in edge.vertices:
                noise_scale = noise_data["noise_scale"]
                edge.vertices[v].co += noise.noise(Vector((edge.vertices[v].co.x, edge.vertices[v].co.y, edge.vertices[v].co.z))) * noise_scale

#This class contains static methods for handling materials, specifically linking materials to objects and adding displacement to the materials.
class TextureHandler:

    @staticmethod
    def material_link(material_name, object):
        object.data.materials.append(bpy.data.materials[material_name])

    @staticmethod
    def material_displacement(material_name, strength):
        material = bpy.data.materials.get(material_name)
        if material is not None:
            material.use_nodes = True
            tree = material.node_tree
            for node in tree.nodes:
                tree.nodes.remove(node)
            bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')
            bsdf.location = 0, 300
            displacement = tree.nodes.new('ShaderNodeDisplacement')
            displacement.inputs['Scale'].default_value = strength
            displacement.location = 400, 300
            tree.links.new(bsdf.outputs[0], displacement.inputs[0])
            tree.links.new(tree.nodes['Material Output'].inputs[0], bsdf.outputs[0])


# It loads configuration data from a JSON file named nucleus.json.
# It loads core objects from Blender files specified in blend_file_paths.
# For each Blender file, it creates a NucleusGenerator instance, creates and merges cores from the loaded objects based on the configuration data.
# After the process, it provides a dictionary containing the created cores.

if __name__ == "__main__":
    # Load configuration data
    with open('nucleus.json', 'r') as f:
        core_config = json.load(f)

    # Load core objects from Blender files
    blend_file_paths = [
        r'c:\Users\Rebeka\Documents\VeA\3ITB\Bakalaura darbs\AIS\asteroid-image-simulator\Targets\Bennu.blend',
        r'c:\Users\Rebeka\Documents\VeA\3ITB\Bakalaura darbs\AIS\asteroid-image-simulator\Targets\Churyumov.blend',
        r'c:\Users\Rebeka\Documents\VeA\3ITB\Bakalaura darbs\AIS\asteroid-image-simulator\Targets\Didymos.blend',
        r'c:\Users\Rebeka\Documents\VeA\3ITB\Bakalaura darbs\AIS\asteroid-image-simulator\Targets\Dimorphos.blend',
        r'c:\Users\Rebeka\Documents\VeA\3ITB\Bakalaura darbs\AIS\asteroid-image-simulator\Targets\Itokawa.blend'
    ]

    for blend_file_path in blend_file_paths:
        with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
            data_to.objects = data_from.objects

        # Create nucleus generator instance
        nucleus_generator = NucleusGenerator()

        # Create and merge cores from objects
        cores = nucleus_generator.create_and_merge_cores_from_objects(data_to.objects, core_config)

        # Now you have a dictionary with created cores
        # You can continue working with these cores as needed
