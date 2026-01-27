import trimesh

mesh = trimesh.load(r'C:\Users\mateu\Desktop\Sem título.ply', force='mesh')
print(f'Vertices: {len(mesh.vertices)}')
print(f'Faces: {len(mesh.faces)}')
print(f'Watertight: {mesh.is_watertight}')
print(f'Volume: {mesh.volume}')

print('\nVertices:')
for i, v in enumerate(mesh.vertices):
    print(f'  {i}: {v}')
