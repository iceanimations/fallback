# Get directory
# Read directory
# Find Name of material in directory files
# format of image filename is <objectname>_<materialname>_<mapname>.<ext>

# possible values of <mapname> = BaseColor, Metallic, Normal, Roughness  --
# NOT "Height" at the moment

# possible types of materials = RedshiftMaterial
# Get From Scene
# Get From Selection

# Respect ways to connect stuff
# Metallic and Roughness should be loaded without color managment
# NormalMap Node to be used in rsNormalMap


import pymel.core as pc
import os
import re


def node_name(node):
    name = node.name()
    name = name.split('|')[-1]
    name = name.split(':')[-1]
    return name


def make_texture_node(path):
    file_node = pc.shadingNode('file', asShader=True)
    place_node = pc.shadingNode('place2dTexture', asShader=True)

    # make connections
    place_node.outUV >> file_node.uvCoord
    place_node.uvFilterSize >> file_node.uvFilterSize
    place_node.coverage >> file_node.coverage
    place_node.translateFrame >> file_node.translateFrame
    place_node.rotateFrame >> file_node.rotateFrame
    place_node.mirrorU >> file_node.mirrorU
    place_node.mirrorV >> file_node.mirrorV
    place_node.stagger >> file_node.stagger
    place_node.wrapU >> file_node.wrapU
    place_node.wrapV >> file_node.wrapV
    place_node.repeatUV >> file_node.repeatUV
    place_node.offset >> file_node.offset
    place_node.rotateUV >> file_node.rotateUV
    place_node.noiseUV >> file_node.noiseUV
    place_node.vertexUvOne >> file_node.vertexUvOne
    place_node.vertexUvTwo >> file_node.vertexUvTwo
    place_node.vertexUvThree >> file_node.vertexUvThree
    place_node.vertexCameraOne >> file_node.vertexCameraOne

    # setting texture name
    file_node.fileTextureName.set(path)
    path_wo, ext = os.path.splitext(path)
    _, basename = os.path.split(path_wo)
    pc.rename(file_node, basename)
    return file_node


def make_raw(file_node):
    file_node.ignoreColorSpaceFileRules.set(1)
    pc.setAttr(file_node + '.cs', "Raw", type="string")
    return file_node


class _BaseImporter(object):
    texture_types = ['.*']
    file_extensions = ['tif', 'png', 'exr', 'jpg', 'jpeg']

    @property
    def node_type(self):
        raise NotImplementedError

    def get_materials(self, sl=False):
        materials = pc.ls(type=self.node_type, sl=sl)
        return materials

    def get_textures(self, material, path, obj=None):
        assert pc.nodeType(material) == self.node_type

        name = node_name(material)
        texs = []

        for tex_type in self.texture_types:
            for ext in self.file_extensions:
                rexp = '%s_?%s_%s\\.%s' % (
                        obj if obj is not None else '[^_]*', name, tex_type,
                        ext)
                for filename in os.listdir(path):
                    match = re.match(rexp, filename, re.I)
                    if match:
                        texs.append(os.path.join(path, match.group()))

        return texs

    def get_obj_name(self, path, node):
        name = node_name(node)
        dirname, basename = os.path.split(path)
        for tex_type in self.texture_types:
            for ext in self.file_extensions:
                rexp = '([^_]*)_?%s_%s\\.%s' % (name, tex_type, ext)
                match = re.match(rexp, basename, re.I)
                if match:
                    return match.group(1)
        return ''

    def get_texture_type(self, path, node):
        name = node_name(node)
        dirname, basename = os.path.split(path)
        rexp = '[^_]*_?%s_(.*)\\..*' % name
        match = re.match(rexp, basename)
        if match:
            return match.group(1)
        return ''

    def get_all_textures(self, path, sl=False):
        nodes = pc.ls(type=self.node_type, sl=sl)
        all_texs = {}

        for node in nodes:
            name = node_name(node)
            texs = self.get_textures(self, node, path)
            node_texs = {}

            for tex in texs:
                obj = self.get_obj_name(name)
                if obj in node_texs:
                    node_texs[obj].append(tex)
                else:
                    node_texs[obj] = [tex]

            if name in all_texs:
                all_texs[name].update(node_texs)
            else:
                all_texs[name] = node_texs

        return all_texs

    def apply_texture(self, material, texture_path, delete_existing=True):
        raise NotImplementedError

    def apply_textures_to_material(self, material, path, obj=None,
                                   tex_types=None, delete_existing=True):
        texs = self.get_textures(material, path, obj)
        if texs and obj is None:
            obj = self.get_obj_name(texs[0], material)
        if tex_types is None:
            tex_types = self.texture_types
        for tex in texs:
            tex_type = self.get_texture_type(tex, material)
            if obj == self.get_obj_name(
                    tex, material) and tex_type in tex_types:
                self.apply_texture(material, tex,
                                   delete_existing=delete_existing)
        return obj

    def apply_all_textures(self, path, sl=False, obj=None, tex_types=None,
                           delete_existing=True):
        materials = self.get_materials(sl=sl)
        for mat in materials:
            obj = self.apply_textures_to_material(
                    mat, path, obj=obj, tex_types=tex_types,
                    delete_existing=delete_existing)
        return obj


class _BaseRedshiftImporter(_BaseImporter):
    texture_types = ['BaseColor', 'Metallic', 'Normal', 'Roughness']

    def apply_texture(self, material, texture_path,
                      delete_existing=True):
        print 'apply_texture', material, texture_path
        texture_type = self.get_texture_type(texture_path, material)
        function = self.application_functions.get(texture_type, None)
        if function is not None:
            material.refl_brdf.set(1)
            return function(self, material, texture_path, delete_existing)

    def apply_basecolor_texture(self, material, texture_path,
                                delete_existing=True):
        file_node = make_texture_node(texture_path)
        if delete_existing:
            for inp in material.diffuse_color.inputs():
                pc.delete(pc.listHistory(inp))
        file_node.outColor >> material.diffuse_color
        return file_node

    def apply_metallic_map(self, material, texture_path,
                           delete_existing=True):
        # make raw and disable color management
        material.refl_fresnel_mode.set(2)
        file_node = make_texture_node(texture_path)
        make_raw(file_node)
        if delete_existing:
            for inp in material.refl_metalness.inputs():
                pc.delete(pc.listHistory(inp))
        file_node.outAlpha >> material.refl_metalness
        file_node.alphaIsLuminance.set(True)
        return file_node

    def apply_normal_map(self, material, texture_path,
                         delete_existing=True):
        # enable Y check!
        nmap = pc.shadingNode('RedshiftNormalMap', asShader=True)
        nmap.tex0.set(texture_path)
        nmap.flipY.set(1)
        if delete_existing:
            for inp in material.bump_input.inputs():
                pc.delete(pc.listHistory(inp))
        nmap.outDisplacementVector >> material.bump_input
        return nmap

    def apply_roughness_map(self, material, texture_path,
                            delete_existing=True):
        # make raw and disable color management
        file_node = make_texture_node(texture_path)
        make_raw(file_node)
        if delete_existing:
            for inp in material.refl_roughness.inputs():
                pc.delete(pc.listHistory(inp))
        file_node.outAlpha >> material.refl_roughness
        file_node.alphaIsLuminance.set(True)
        return file_node

    application_functions = {
            'BaseColor': apply_basecolor_texture,
            'Metallic': apply_metallic_map,
            'Normal': apply_normal_map,
            'Roughness': apply_roughness_map
    }


class RedshiftMaterialImporter(_BaseRedshiftImporter):
    node_type = 'RedshiftMaterial'


class RedshiftArchitecturalImporter(_BaseRedshiftImporter):
    node_type = 'RedshiftArchitectural'


class SubstanceImporter(object):
    __classes = [RedshiftMaterialImporter, RedshiftArchitecturalImporter]

    def __init__(self):
        self.type_dict = {cls.node_type: cls for cls in self.__classes}

    def get_node_types(self):
        return [cls.node_type for cls in self.__classes]

    def get_importer_classes(self):
        return self.__classes.copy()

    def get_materials(self, sl=False):
        materials = []
        for cls in self.__classes:
            materials.append(cls().get_materials(sl=sl))
        return materials

    def get_importer_class(self, material):
        return self.__classes.get(pc.nodeType(material))

    def apply_all_textures(self, path, sl=False, obj=None, tex_types=None):
        file_nodes = []
        for cls in self.__classes:
            file_node = cls().apply_all_textures(
                    path, sl=sl, obj=obj, tex_types=tex_types)
            file_nodes.append(file_node)
        return file_nodes


if __name__ == "__main__":
    substance_texture_path = (
            r'L:\LU\Prince_Choc_5\assets\environment\mustachio_lair_int'
            r'\sources\substance\side\textures'
    )
    path = r'D:\talha.ahmed\Documents\maya\projects\default\scenes\texture'
    path = r'L:\LU\Prince_Choc_5\assets\environment\mustachio_factory_int\sources\substance\Floor_ResearchArea\texture'
    importer = SubstanceImporter()
    importer.apply_all_textures(path)
