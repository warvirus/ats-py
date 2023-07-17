# /usr//bin/python
# -*- coding: utf-8 -*-

# __all__ = ['kiwoom_api']
import pandas


# main lib
# if __package__ is None:
from .kiwoom import *
from .ui import (
        REAL_INVESTMENT,
        SIM_INVESTMENT, 

        user_info,
        app_ui,
    )

from .tools import *
from .version import (
    __version__,
    __author__,
)

from .webkiwoom import *
# __all__ =[
#    "__version__",
#    "__author__",
#]

try:
    import platform

    os = platform.system()
    if os == "Darwin":
        # fonts = [x.name for x in fm.fontManager.ttflist if 'AppleGothic' in x.name]
        #plt.rc('font', family="AppleGothic")
        #draw
        pass
    else:
        # fonts = [x.name for x in fm.fontManager.ttflist if 'Malgun Gothic' in x.name]
        # plt.rc('font', family="Malgun Gothic")
        pass
except:
    pass


if __name__ == '__main__':
    print(__version__)
    