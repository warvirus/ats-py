# ats-py
키움증권API 기반으로 작성된 증권트레이드

기본적으로 파이선에서 설치해야 할 모듈들이다.

pip install tabulate
pip install eventhandler
pip install plotly
pip install Slacker
# pip install pywebview
pip install PyQtWebkit

# 암호화
# pip install pycryptodomex
# pip install crypto
pip install pycrypto

키움증권 API는 WIN32 지원하기 때문에 conda 환경 설정에서 win32 로 설정해야 한다.
1. win-32, Python 2.7 설치

- conda create -n py27_32
- conda activate py32_32
- conda config --env --set subdir win-32
- conda install python=2.7

2. win-64, Python 3.7 설치

- conda create -n py32_64
- conda activate py37_64
- conda config --env --set subdir win-64
- conda install python=3.7
