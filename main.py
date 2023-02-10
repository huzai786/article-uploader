import os.path
import sys

import PySimpleGUI as sg

from api.automate import save_keywords, process_keywords
import config

if not config.APPLICATION_PASSWORD or not config.SITE_URL or not config.USERNAME:
    raise Exception("Please Enter Configuration settings!")

DB_NAME = "db.json"

keywords = []

def main_window():
    layout = [
        [sg.Text("Automatically upload wordpress articles")],
        [sg.In(), sg.FilesBrowse(file_types=(("Text Files", "*.txt"),), key="file")],
        [sg.Button("Select File and Save Keywords", key='SELECT'), sg.Text("file selected: no file selected",
                                                                    key='SELECTED_FILE')],
        [sg.Button("START", key='START'), sg.P(), sg.Button("STOP", key='STOP', disabled=True)],
        [sg.Text(key='db')]
    ]
    window = sg.Window("upload posts", layout, finalize=True)
    return window

window = main_window()
if os.path.exists(DB_NAME):
    print("DataBase Found!")
else:
    print('No DataBase Found!')

while True:
    event, value = window.read()

    if event in ('Cancel', sg.WINDOW_CLOSED):
        break

    if event == 'SELECT':
        path = value['file']
        if not path:
            sg.popup_error("no file selected!")
            continue
        if not os.path.exists(path):
            sg.popup_error("File Not Found!")
            continue

        with open(path, 'r', encoding='utf-8') as f:
            data = f.readlines()

        keywords = (i.strip('\n') for i in data if i != "")
        save_keywords(DB_NAME, keywords)
        print("Saving keywords")
        window.close()
        window = main_window()
        window['SELECTED_FILE'].update(path)

    if event == 'START':
        if not os.path.exists(DB_NAME):
            sg.popup_error("Select keyword file!")
            continue
        window['START'].update(disabled=True)
        window['STOP'].update(disabled=False)

        window.perform_long_operation(lambda: process_keywords(DB_NAME), end_key="LONG_PROCESS")

    if event == "LONG_PROCESS":
        sg.popup_auto_close("Completed")

    if event == "STOP":
        if not os.path.exists(DB_NAME):
            sg.popup_error("Select keyword file!")
            continue
        sys.exit()

window.close()