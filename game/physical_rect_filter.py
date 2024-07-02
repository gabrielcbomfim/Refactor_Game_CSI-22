def physical_rect_filter(tiles):
    valid = []
    for tile in tiles:
        for tile_type in tile[0]:
            if tile_type[0] in ['grass_tileset', 'dirt_tileset']:
                valid.append(tile[1])
                break
    return valid