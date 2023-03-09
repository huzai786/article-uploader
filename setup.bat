@echo off

echo Creating virtual environment %env_name%...
virtualenv env

echo Activating virtual environment...
call env\Scripts\activate.bat

echo Installing requirements...
pip install -r requirements.txt

echo Deactivating virtual environment...
deactivate

echo Setup complete.
@pause