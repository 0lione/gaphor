"""Parse a SysML Gaphor Model and generate a SysML data model."""

from collections import deque
from typing import Deque, Dict, List, Optional, Set, TextIO, Tuple

from gaphor import UML
from gaphor.core.modeling.element import Element
from gaphor.core.modeling.elementfactory import ElementFactory
from gaphor.storage import storage
from gaphor.UML.modelinglanguage import UMLModelingLanguage


def type_converter(association, enumerations: Dict = {}) -> Optional[str]:
    type_value = association.typeValue
    if type_value is None:
        return None
        # raise ValueError(
        #     f"ERROR! type is not specified for property {association.name}"
        # )
    if type_value.lower() == "boolean":
        return "int"
    elif type_value.lower() in ("integer", "unlimitednatural"):
        return "int"
    elif type_value.lower() == "string":
        return "str"
    elif type_value.endswith("Kind") or type_value.endswith("Sort"):
        # e = list(filter(lambda e: e["name"] == type_value, list(enumerations.values())))[0]
        return None
    else:
        return str(type_value)


def write_attributes(cls: UML.Class, filename: TextIO) -> None:
    if not cls.attribute or not cls.attribute[0].name:
        filename.write("    pass\n\n")
    else:
        for a in cls.attribute["not it.association"]:  # type: ignore
            type_value = type_converter(a)
            filename.write(f"    {a.name}: attribute[{type_value}]\n")
        for a in cls.attribute["it.association"]:  # type: ignore
            type_value = type_converter(a)
            if a.name == "baseClass":
                meta_cls = a.association.ownedEnd.class_.name
                filename.write(f"    {meta_cls}: association\n")
            else:
                filename.write(f"    {a.name}: relation_one[{type_value}]\n")
        for o in cls.ownedOperation:
            filename.write(f"    {o}: operation\n")


def filter_uml_classes(
    classes: List[UML.Class],
) -> Tuple[List[UML.Class], List[UML.Class]]:
    """Remove classes that are part of UML."""
    uml_directory: List[str] = dir(UML.uml)
    filtered_classes = [
        cls
        for cls in classes
        if cls.name and cls.name[0] != "~" and cls.name not in uml_directory
    ]
    uml_classes = [cls for cls in classes if cls.name in uml_directory]
    return filtered_classes, uml_classes


def create_class_trees(classes: List[UML.Class]) -> Dict[UML.Class, List[UML.Class]]:
    """Create a tree of UML.Class elements.

    The relationship between the classes is a generalization. Since the opposite
    relationship, `cls.specific` is not currently stored, only the children
    know who their parents are, the parents don't know the children.

    """
    trees = {}
    for cls in classes:
        trees[cls] = [g for g in cls.general]
    return trees


def create_referenced(classes: List[UML.Class]) -> List[UML.Class]:
    """UML.Class elements that are referenced by others.

    We consider a UML.Class referenced when its child UML.Class has a
    generalization relationship to it.

    """
    referenced = []
    for cls in classes:
        for gen in cls.general:
            referenced.append(gen)
    return referenced


def find_root_nodes(
    trees: Dict[UML.Class, List[UML.Class]], referenced: List[UML.Class]
) -> List[UML.Class]:
    """Find the root nodes of tree models.

    The root nodes aren't generalizing other UML.Class objects, but are being
    referenced by others through their own generalizations.

    """
    return [key for key, value in trees.items() if not value and key in referenced]


def breadth_first_search(
    trees: Dict[UML.Class, List[UML.Class]], root: UML.Class
) -> List[UML.Class]:
    """Perform Breadth-First Search."""

    explored: List[UML.Class] = []
    queue: Deque[UML.Class] = deque()
    queue.appendleft(root)
    while queue:
        node = queue.popleft()
        if node not in explored:
            explored.append(node)
            neighbors: List[UML.Class] = []
            for key, value in trees.items():
                if node in value:
                    neighbors.append(key)
            if neighbors:
                for neighbor in neighbors:
                    queue.appendleft(neighbor)
    return explored


def generate(filename, outfile=None, overridesfile=None) -> None:
    element_factory = ElementFactory()
    modeling_language = UMLModelingLanguage()
    with open(filename):
        storage.load(
            filename, element_factory, modeling_language,
        )
    with open(outfile, "w") as f:
        f.write(f"from gaphor.UML import Element\n")
        f.write(f"from gaphor.core.modeling.properties import attribute, association\n")
        f.write(
            f"from gaphor.core.modeling.properties import relation_one, relation_many\n"
        )

        classes: List = element_factory.lselect(lambda e: e.isKindOf(UML.Class))

        classes, uml_classes = filter_uml_classes(classes)
        for cls in uml_classes:
            f.write(f"from gaphor.UML import {cls.name}\n\n")

        trees = create_class_trees(classes)
        referenced = create_referenced(classes)
        root_nodes = find_root_nodes(trees, referenced)

        cls_written: Set[str] = set()
        for root in root_nodes:
            classes_found: List = breadth_first_search(trees, root)
            for cls in classes_found:
                if cls.name not in cls_written:
                    if cls.general:
                        f.write(
                            f"class {cls.name}("
                            f"{', '.join(g.name for g in cls.general)}):\n"
                        )
                    else:
                        f.write(f"class {cls.name}:\n")
                    cls_written.add(cls.name)
                    write_attributes(cls, filename=f)

        for cls, generalizations in trees.items():
            if not generalizations:
                if cls.name not in cls_written:
                    f.write(f"class {cls.name}:\n")
                    write_attributes(cls, filename=f)
                    cls_written.add(cls.name)

    element_factory.shutdown()
