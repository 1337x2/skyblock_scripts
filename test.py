from minescript import entities
import time

entities_list = entities(nbt=True)

for entity in entities_list:
    print(f"\n=== {entity.type} ===")
    print(f"Name: {entity.name}")
    print(f"NBT: {entity.nbt}")
