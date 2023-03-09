import requests
import PySimpleGUI as sg
from api.article import html_format_data, add_article, current_keywords_posted
from api.extract import extract_youtube

sess = requests.Session()

def process(client, keyword):
    links = extract_youtube(keyword)
    if links:
        html = html_format_data(links, keyword)

        if add_article(keyword, html, client):
            return True
        else:
            return False
    else:
        return False


def process_keywords(file_path, window: sg.Window):
    with open(file_path, 'r', encoding='utf-8') as f:
        keywords_left = [i.strip() for i in f.readlines()]

    window["-OUTPUT-"].update("Getting current Keywords from the wordpress api. (Don't stop the script)" + '\n', append=True, text_color="black")
    uploaded_keywords = current_keywords_posted()

    window["-OUTPUT-"].update("Removing already uploaded keywords.  (Don't stop the script)" + '\n', append=True, text_color="black")
    for k in uploaded_keywords:
        try:
            keywords_left.remove(k)
        except ValueError:
            pass

    window["-OUTPUT-"].update("Saving keywords  (Don't stop the script)" + '\n', append=True, text_color="black")
    with open(file_path, 'w', encoding='utf-8') as f:
        for k in keywords_left:
            f.write(k + '\n')

    window["-OUTPUT-"].update("You can stop the script now." + '\n', append=True, text_color="black")
    keywords_length = len(keywords_left)
    for i, kw in enumerate(keywords_left):
        if process(sess, kw):
            keywords_length -= 1
        s = display_status(kw, i, keywords_length, process)
        window["-OUTPUT-"].update(s + '\n', append=True, text_color="black")
    return

def display_status(keyword, current_completed_count, total_keywords, posted):
    output_string = f"""
    |===============================================|
    |   Total Keywords Left:  {total_keywords}
    |   Current Status: {current_completed_count + 1} Completed!
    |   Current keyword: {keyword}        
    |   Posted:  {"Yes" if posted else "No"}          
    |===============================================|
    """
    return output_string



