from numpy import shape, zeros, amin, uint8


def convert_heightmap_into_RGB(heightmap, brightness=1, levels=None, rgb_dict=None):
    """
    convert_heightmap_into_RGB - converter of 2D array of float values into same size 2D array of [R,G,B] elements
    :param heightmap: 2D heightmap
    :param brightness: brightness of colors for output (range from 0 to 1)
    :param levels: relative points of next levels of color gradient change
                    from 0 - 1 (values out of range are normalized)
                    You can omit putting 0 and 1 at the edges of list
    :param rgb_dict: dictionary with tuples for levels for each color
                    each tuple represents (multiplier for heightmap values, offset for multiplied values)
                    Default setup for dictionary:
                    'R': [(2, -1), (0.95, -0.3), (0.1, 0.65), (-0.75, 0.75)],
                    'G': [(1, 0), (0.55, 0.1), (-0.25, 0.65), (-0.4, 0.4)],
                    'B': [(2, 0), (0, 0), (0, 0), (0, 0)]
                    Each tuple is corresponding to each level from [0-level1-level2-...-1] list
    :return: 2D array of same size as heightmap, with RGB elements ([R, G, B])
    """
    # default values
    if levels is None:
        levels = [0.3, 0.5, 0.5]
    else:
        levels = [(x if 0 <= x <= 1 else 0) for x in levels]
    if rgb_dict is None:
        rgb_dict = {
            'R': [(2, -1), (0.95, -0.3), (0.1, 0.65), (-0.75, 0.75)],
            'G': [(1, 0), (0.55, 0.1), (-0.25, 0.65), (-0.4, 0.4)],
            'B': [(2, 0), (0, 0), (0, 0), (0, 0)]
        }

    try:
        heightmap[2, 2]
    except IndexError:
        print("Shape of the heightmap need to be greater than 1x1")
        return -1

    # normalize heightmap values to be in range 0-1
    heightmap = (heightmap.astype(float) - amin(heightmap)) / heightmap.ptp()

    # convert relative values of levels into absolute values between 0-1
    if len(levels) > 1:
        for i in range(1, len(levels)):
            levels[i] = levels[i] * (1 - levels[i-1]) + levels[i-1]
    if levels[0] != 0:
        levels = [0.0] + levels
    if levels[-1] != 1:
        levels = levels + [1.0]

    # that assures that colors are properly displayed
    brightness = brightness if 0 <= brightness <= 1 else 1

    RGB_map = zeros((shape(heightmap)[0], shape(heightmap)[1], 3), dtype=float)

    for i in range(1, len(levels)):
        for key in rgb_dict:
            tmp_map = heightmap.copy()
            tmp_map[heightmap > levels[i]] = levels[i]
            tmp_map[heightmap <= levels[i-1]] = levels[i-1]
            if tmp_map.ptp() != 0:
                tmp_map = (tmp_map - amin(tmp_map)) / tmp_map.ptp()
            tmp_map = tmp_map * rgb_dict[key][i-1][0] + rgb_dict[key][i-1][1]
            # going over 0-1 range causes glitches with colors
            tmp_map[tmp_map < 0] = 0
            tmp_map[tmp_map > 1] = 1
            # zero values out of level so all of them can be added easily
            tmp_map[heightmap > levels[i]] = 0
            tmp_map[heightmap < levels[i-1]] = 0
            if key == 'R':
                RGB_map[:, :, 0] += tmp_map
            if key == 'G':
                RGB_map[:, :, 1] += tmp_map
            if key == 'B':
                RGB_map[:, :, 2] += tmp_map

    RGB_map *= brightness * 255

    return RGB_map.astype(uint8)
