## This file is for functions that exist independently of operators ##

import random
import bpy

# Given a value and a range, get a variation on that number
def get_varied_scale(value: float, offset: float) -> float:
    min_scale = value - offset
    max_scale = value + offset
    return random.uniform(min_scale, max_scale)


def move_to_collection(name: str, obj) -> None:
    active_collection = bpy.context.collection
    target_collection = None

    if name in bpy.data.collections:
        target_collection = bpy.data.collections[name]
    else:
        target_collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(target_collection)

    target_collection.objects.link(obj)

    if obj.name in active_collection.objects:
        active_collection.objects.unlink(obj)