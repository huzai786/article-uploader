import json
import os.path
import shutil
import sys

import PySimpleGUI as sg

from api.automate import process_keywords
import config

if not config.APPLICATION_PASSWORD or not config.SITE_URL or not config.USERNAME or not config.CATEGORY_ID:
    raise Exception("Please Enter Configuration settings!")

if isinstance(config.CATEGORY_ID, str):
    raise Exception("Write Integer for Category ID.")

sg.theme("LightBlue2")
config_path = os.path.join(os.getcwd(), "config.json")
if not os.path.exists(config_path):
    f = open(config_path, 'w')
    json.dump({"keywords_file_path": ""}, f)
    f.close()

def get_keywords_path(config_path):
    with open(config_path, 'r') as f:
        data = json.load(f)
        return data

def update_keywords_path(config_path, file_path):
    with open(config_path, 'r') as rf:
        data = json.load(rf)
    with open(config_path, 'w') as wf:
        if file_path:
            data["keywords_file_path"] = file_path
        else:
            data["keywords_file_path"] = ""
        json.dump(data, wf)

def check_keywords_path():
    keyword_file_path = get_keywords_path(config_path).get("keywords_file_path")
    keywords_uploaded = keyword_file_path if keyword_file_path else ""
    return keywords_uploaded

def main_window():
    layout = [
        [sg.Text("Upload Wordpress Articles", font=("Sans Serif", 20, "bold"))],
        [sg.HSep(color="black", pad=6)],
        [sg.Text("Browse keywords file: ", font=("Sans Serif", 10, "bold")), sg.In(key="file", disabled=True), sg.Push(),
         sg.FilesBrowse(file_types=(("Text Files", "*.txt"),), size=(8, 1), key="FILE_BROWSE", target=(sg.ThisRow, -2))],
        [sg.Button("Select File", key='SELECT'), sg.Push(),
         sg.Button("Delete File", disabled=True, key="DELETE_FILE")],
        [sg.Text("Output:", font=("Sans serif", 13, "bold"))],
        [sg.MLine(size=(550, 13), key="-OUTPUT-", autoscroll=True)],
        [sg.VPush()],
        [sg.Button("START", key='START', size=(14, 1)), sg.P(), sg.Button("STOP", key='STOP', disabled=True, size=(14, 1))],
    ]
    window = sg.Window("upload posts", layout, finalize=True, size=(700, 420))
    return window

keywords_saved = check_keywords_path()
window = main_window()
display_file = True
while True:
    event, value = window.read(timeout=400)
    if event in ('Cancel', sg.WINDOW_CLOSED):
        break
    if keywords_saved:
        window["DELETE_FILE"].update(disabled=False)
        window["FILE_BROWSE"].update(disabled=True)
        if display_file:
            window["-OUTPUT-"].update(value=f"keyword File: {keywords_saved}" + '\n')
            display_file = False
    else:
        window["DELETE_FILE"].update(disabled=True)
        window["FILE_BROWSE"].update(disabled=False)

    if event == "DELETE_FILE":
        if sg.popup_ok_cancel("Are you sure to delete keyword file.") == "OK":
            os.unlink(keywords_saved)
            update_keywords_path(config_path, file_path=None)
            keywords_saved = check_keywords_path()
            window["file"].update(value="")
            window["-OUTPUT-"].update(value=f"File Deleted!" + '\n', append=True)
            continue

    if event == 'SELECT':
        keywords_file_path = value['file']
        if not keywords_file_path:
            sg.popup_error("no file selected!")
            continue
        if not os.path.exists(keywords_file_path):
            sg.popup_error("File Not Found!")
            continue

        destination_path = os.path.join(os.getcwd(), "keywords.txt")
        shutil.copy(keywords_file_path, destination_path)
        update_keywords_path(config_path, destination_path)
        keywords_saved = check_keywords_path()
        sg.popup_auto_close("File Saved!")
        window["-OUTPUT-"].update(value=f"File Found: {keywords_file_path}" + '\n', append=True)
        window["-OUTPUT-"].update(f"Saving File" + '\n', append=True)

    if event == 'START':
        if sg.popup_ok_cancel("Start Posting") != "OK":
            continue
        if not keywords_saved:
            sg.popup_error("Select keyword file!")
            continue
        window['START'].update(disabled=True)
        window['STOP'].update(disabled=False)
        window["-OUTPUT-"].update("Starting Scraping!" + '\n', append=True, text_color="black")
        window.perform_long_operation(lambda: process_keywords(keywords_saved, window), end_key="LONG_PROCESS")

    if event == "LONG_PROCESS":
        sg.popup_auto_close("Completed")
        window['START'].update(disabled=False)
        window['STOP'].update(disabled=True)

    if event == "STOP":
        if not keywords_saved:
            sg.popup_error("Select keyword file!")
            continue
        window["-OUTPUT-"].print("Stopping!", text_color="black")
        sys.exit()

window.close()