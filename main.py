import os.path

import PySimpleGUI as sg

from api.automate import process_keywords

layout = [
    [sg.Text("Automatically upload wordpress articles")],
    [sg.In(), sg.FilesBrowse(file_types=(("Text Files", "*.txt"),), key="file")],
    [sg.Button("Select File", key='SELECT'), sg.Text("file selected: no file selected", key='SELECTED_FILE')],
    [sg.Button("Start Uploading", key='UPLOAD'), sg.Cancel()],
    [sg.Text(key='output')]
]

window = sg.Window("upload posts", layout)
keywords = []
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

        with open(path, 'r') as f:
            data = f.readlines()
        keywords = [i.strip('\n') for i in data]

        print("found:", len(keywords), "keywords")
        window['SELECTED_FILE'].update(path)

    if event == 'UPLOAD':
        if window['SELECTED_FILE'] == "":
            sg.popup_error("No File Selected")
            continue
        window.perform_long_operation(lambda: process_keywords(keywords), end_key="LONG_PROCESS")

    if event == 'LONG_PROCESS':
        record = value["LONG_PROCESS"]
        if record.get('uncompleted'):
            with open('uncompleted.txt', 'w') as f:
                for i in record['uncompleted']:
                    f.write(i+'\n')

        window['output'].update(f"uncompleted: {len(record.get('uncompleted'))}")
        sg.popup_auto_close("Done")

window.close()