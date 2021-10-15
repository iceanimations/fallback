from .substance_importer import (
        SubstanceImporter,
        RedshiftArchitecturalImporter,
        RedshiftMaterialImporter
)


def apply_to_selected(path):
    importer = SubstanceImporter()
    importer.apply_all_textures(path, sl=True)


def apply_to_all(path):
    importer = SubstanceImporter()
    importer.apply_all_textures(path)
