echo @off
IF EXIST env (
    echo Virtualenv created.
    echo Instantiating virtualenv
    call env/Scripts/Activate.bat
    echo starting GUI
    call py main.py
    @pause
) ELSE (
    echo Virtualenv does not exist.
    @pause
  
)
