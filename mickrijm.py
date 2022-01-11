import os

import bs4
import html

from urllib import request, parse


class RijmStatusException(Exception):
    pass

class RijmEmptyException(Exception):
    pass

def rijm_word(word):
    url = "https://rijmwoordenboek.nl/rijm"
    data = {
        "RhymeWord": word, 
        "RhymeHistory": "", 
        "RhymeButton": "RIJM!"
    }

    req = request.Request(url, method="POST", data=parse.urlencode(data).encode())
    resp = request.urlopen(req)
    status = resp.status

    if status != 200:
        raise RijmStatusException("status != 200 ({})".format(status))
    
    text = resp.read()
    soup = bs4.BeautifulSoup(text, "html.parser")

    words = soup.find(id='rhymeResultsWords')
    word_results = []

    if words:
        for line in words.stripped_strings:
            word_results.append(html.escape(line.replace(' ', '').replace('\n', '')))
    else:
        raise RijmEmptyException("No results for '{}'".format(word))

    return word_results

try:
    import sublime
    import sublime_plugin

    class RijmWordCommand(sublime_plugin.TextCommand):
        def run(self, edit):
            view = self.view

            # Only check for first selection
            sel = view.sel()[0]
            line = view.line(sel)

            if sel.empty():
                sel = view.word(sel)

            try:
                word_results = rijm_word(view.substr(sel))
                print(view.substr(sel), ':', word_results)
                
                def add_next_line(word_results_index):
                    if word_results_index != -1:
                        print()
                        view.insert(edit, line.end(), '\n{}'.format(word_results[word_results_index]))
                view.show_popup_menu(word_results, on_select=add_next_line)
            except RijmEmptyException as e:
                view.show_popup(str(e))
            except Exception as e:
                view.show_popup('Exception: {}'.format(str(e)))
                raise e
except ModuleNotFoundError as e:
    pass

if __name__ == '__main__':
    import sys
    word = None
    if len(sys.argv) <= 2:
        if len(sys.argv) < 2:
            word = input('Word to rijm?\n> ')
        else:
            word =  sys.argv[1]
        word_results = rijm_word(word)
        print('\n'.join(word_results))
    else:
        for word in sys.argv[1:]:
            print('{}:'.format(word))
            try:
                word_results = rijm_word(word)
                print('\n'.join(word_results))
            except RijmEmptyException as e:
                print(str(e))