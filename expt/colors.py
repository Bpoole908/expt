import sys
_thismodule = sys.modules[__name__]

# populate all matplotlib named colors as module attributes.
# https://matplotlib.org/examples/color/named_colors.html
from matplotlib import colors as mcolors
_colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

for color_name in _colors:
    setattr(_thismodule, color_name, color_name)

del sys
del _thismodule


# Sensible default color sets that are more distinguishable: 17 colors
# https://matplotlib.org/3.1.0/gallery/color/named_colors.html
DefaultColors = (
    'dimgray',
    'dodgerblue',
    'limegreen',
    'coral',
    'gold',
    'lightpink',
    'brown',
    'red',
    'purple',
    'green',
    'cadetblue',
    'burlywood',
    'royalblue',
    'violet',
    'lightseagreen',
    'yellowgreen',
    'sandybrown',
)


try:
    from pandas.plotting._matplotlib.style import _get_standard_colors
except:
    # support older pandas version as well
    from pandas.plotting._style import _get_standard_colors

get_standard_colors = _get_standard_colors
