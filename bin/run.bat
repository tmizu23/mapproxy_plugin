cd /d %~dp0
call mypython\Scripts\activate.bat

REM �x�N�g���^�C���p�ݒ�(mapnik)
REM mapnik���C���X�g�[�������t�H���_���w�肵�Ă�������
set MAPNIK_HOME=C:\mapnik-v2.2.0

set PATH=%MAPNIK_HOME%\lib;%MAPNIK_HOME%\bin;%PATH%
set PYTHONPATH=%MAPNIK_HOME%\python\2.7\site-packages;%PYTHONPATH%

start "mapproxy server"/min mapproxy-util serve-multiapp-develop %1
