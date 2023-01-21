import sys
from ast import operator
import os
import re
import string
import nltk.stem as ns
import nltk
import tkinter
import tkinter as tk
import json
import ast
nltk.download('punkt')

Iindex = {}
Pindex = {}
pstemmer = ns.PorterStemmer()
dataDict = {}
stoplist = []
folderpath = r'C:\\Users\\User\\Desktop\\A1\\Abstracts'
docs = []
docs = [i for i in range(1, 448)]
flag = 0

# regex and nltk used to remove punctuations


def remove_punctuations(contents):
    res = re.sub(r',', ' ', contents)
    res = re.sub(r'-', ' ', res)
    res = re.sub(r'[^\w\s]', '', res)
    translator = str.maketrans('', '', string.punctuation)
    x = res.translate(translator)
    return nltk.word_tokenize(x)


def case_fold(contents):
    contents = contents.casefold()
    return contents


def remove_stoplist_word(tokens):
    stoplist = open('Stopword-List.txt').read().split()
    tokens = [token for token in tokens if token not in stoplist]
    return tokens

# porter stemmer used for stemming tokens


def stem_tokens(tokens):
    stemmed_words = [pstemmer.stem(token) for token in tokens]
    return stemmed_words

# this function calls routines/functions to tokenize,remove stop words,stemm tokens and add them to ditcionary


def preprocessor(contents):
    for content in contents:
        tokens = remove_punctuations(content[1])
        filtered_tokens = remove_stoplist_word(tokens)
        stemmed_tokens = stem_tokens(filtered_tokens)
        filtered_tokens1 = remove_stoplist_word(stemmed_tokens)
        dataDict[content[0]] = filtered_tokens1
    return dataDict


def get_vocabulary(data):
    tokens = []
    for token_list in data.values():
        tokens = tokens + token_list
    # This function is used to find the frequency of words within a text. It returns a dictionary. We need to pass keys and values to get the data.
    fdist = nltk.FreqDist(tokens)
    return list(fdist.keys())


def inverted_index(data2, data):
    for word in data2:
        for dId, tokens in data.items():
            if word in tokens:
                if word in Iindex.keys():
                    Iindex[word].append(dId)
                else:
                    Iindex[word] = [dId]
    return Iindex


def positional_index(data2, data):
    for word in data2:
        for key, value in data.items():
            for pos in range(len(value)):
                if word == value[pos]:
                    if word not in Pindex.keys():
                        Pindex[word] = {}
                    if key not in Pindex[word]:
                        Pindex[word][key] = []
                    Pindex[word][key].append(pos)
    return Pindex


def filereader():
    global Iindex
    global Pindex
    words = []
    count = 1
    file_exists = os.path.exists("inverted_index.txt")
    if file_exists:  # if file exists load inverted index from file
        with open('inverted_index.txt') as f:
            data = f.read()
            Iindex = ast.literal_eval(data)
    else:  # else create and save index to file
        for f in os.listdir(folderpath):
            data = case_fold(open('C:\\Users\\User\\Desktop\\A1\\Abstracts\\' +
                                  f, 'r', encoding='utf-8', errors='ignore').read())
            docs.append(int(f[:-4]))
            words.append((int(f[:-4]), data))
            count += 1
        data = preprocessor(words)
        data2 = get_vocabulary(data)
        inverted_index(data2, data)
        with open('inverted_index.txt', 'w') as f:
            f.write(json.dumps(Iindex))
        f.close()
    file_exists = os.path.exists("positional_index.txt")
    if file_exists:  # if file exists load positional index from file
        with open('positional_index.txt') as f:
            data = f.read()
            Pindex = ast.literal_eval(data)
    else:  # else create and save index to file
        for f in os.listdir(folderpath):
            data = case_fold(open('C:\\Users\\User\\Desktop\\A1\\Abstracts\\' +
                                  f, 'r', encoding='utf-8', errors='ignore').read())
            docs.append(int(f[:-4]))
            words.append((int(f[:-4]), data))
            count += 1
        data = preprocessor(words)
        data2 = get_vocabulary(data)
        positional_index(data2, data)
        with open('positional_index.txt', 'w') as f:
            f.write(json.dumps(Pindex))
        f.close()
    return words

# handle proximity queries


def processPQuery(query):
    print('pqqq')
    queryterms = []
    stemmed_Qterms = []
    x = case_fold(query)
    queryterms = nltk.word_tokenize(x)
    stemmed_Qterms = stem_tokens(queryterms)
    print(stemmed_Qterms)
    dict1 = Pindex[stemmed_Qterms[0]]
    dict2 = Pindex[stemmed_Qterms[1]]
    # since the index was written in json format in file,keys were converted to string,hence this line of code converts them back to integer
    dict1 = {int(k): [int(i) for i in v] for k, v in dict1.items()}
    dict2 = {int(k): [int(i) for i in v] for k, v in dict2.items()}
    a = stemmed_Qterms[2]
    k = int(a[1])
    print(k)
    tp1 = set(dict1)
    tp2 = set(dict2)
    print(tp1, '\n', tp2)
    res = tp1.intersection(tp2)
    tp1 = tp1-res
    tp2 = tp2-res
    for f in tp1:
        dict1.pop(f)
    for f in tp2:
        dict2.pop(f)
    ans = set()
    for f in dict2:
        for pos in dict2[f]:
            print(range(pos-k-1, pos+k+1), dict1[f])
            res = set(range(pos-k-1, pos+k+1)).intersection(dict1[f])
            if len(res):
                ans.add(f)

    return list(ans)

# handle general queries


def processQeury(query):
    queryterms = []
    stemmed_Qterms = []
    operators = ['and', 'not', 'or']
    x = case_fold(query)
    queryterms = remove_punctuations(x)
    stemmed_Qterms = stem_tokens(queryterms)
    print(stemmed_Qterms)
    if len(stemmed_Qterms) == 1:
        print('hey')
        res = Iindex[stemmed_Qterms[0]]
        print(sorted(res))
        return res
    i = 0
    res1 = []
    res2 = []
    ans = []
    ans2 = []
    for token in stemmed_Qterms:
        if token in operators:
            if i <= 1:
                if token == 'and':
                    if stemmed_Qterms[i-1] in Iindex.keys() and stemmed_Qterms[i+1] in Iindex.keys() and stemmed_Qterms[i+1] not in operators:  # t1 and t2
                        res1 = Iindex[stemmed_Qterms[i-1]]
                        res2 = Iindex[stemmed_Qterms[i+1]]
                        ans = [value for value in res1 if value in res2]
                        print('hey')
                        print(sorted(ans))
                    # t1 and not t2
                    elif stemmed_Qterms[i-1] in Iindex.keys() and stemmed_Qterms[i+2] in Iindex.keys() and stemmed_Qterms[i+1] in operators:
                        res1 = Iindex[stemmed_Qterms[i-1]]
                        res2 = Iindex[stemmed_Qterms[i+2]]
                        res2 = [value for value in docs if value not in res2]
                        ans = [value for value in res1 if value in res2]
                        print(sorted(ans))
                elif token == 'or':  # t1 or t2
                    if stemmed_Qterms[i-1] in Iindex.keys() or stemmed_Qterms[i+1] in Iindex.keys() and stemmed_Qterms[i+1] not in operators:  # t1 or t2
                        res1 = Iindex[stemmed_Qterms[i-1]]
                        res2 = Iindex[stemmed_Qterms[i+1]]
                        ans = res1 + list(set(res2) - set(res1))
                        print(sorted(ans))
                    # t1 or not t2
                    elif stemmed_Qterms[i-1] in Iindex.keys() or stemmed_Qterms[i+2] in Iindex.keys() and stemmed_Qterms[i+1] in operators:
                        res1 = Iindex[stemmed_Qterms[i-1]]
                        res2 = Iindex[stemmed_Qterms[i+2]]
                        res2 = [value for value in docs if value not in res2]
                        ans = res1 + list(set(res2) - set(res1))
                        print(sorted(ans))
                elif token == 'not':  # not t1
                    res1 = Iindex[stemmed_Qterms[i+1]]
                    print(res1)
                    ans = [value for value in docs if value not in res1]
                    print(sorted(ans))
            else:
                if token == 'and':  # t1 and t2 and t3 / t1 or t2 and t3
                    if stemmed_Qterms[i+1] not in operators:
                        res1 = Iindex[stemmed_Qterms[i+1]]
                        ans2 = [value for value in ans if value in res1]
                        print(sorted(ans2))
                        ans = ans2
                        break
                    else:  # t1 and t2 and not t3 / t1 or t2 and not t3
                        res1 = Iindex[stemmed_Qterms[i+2]]
                        res1 = [value for value in docs if value not in res1]
                        ans2 = [value for value in ans if value in res1]
                        print(sorted(ans2))
                        ans = ans2
                        break
                elif token == 'or':
                    # t1 and t2 or t3 / t1 or t2 or t3
                    if stemmed_Qterms[i+1] not in operators:
                        res1 = Iindex[stemmed_Qterms[i+1]]
                        ans2 = ans + list(set(res1) - set(ans))
                        print(sorted(ans2))
                        ans = ans2
                        break
                    else:  # t1 and t2 or not t3 / t1 or t2 or not t3
                        res1 = Iindex[stemmed_Qterms[i+2]]
                        res1 = [value for value in docs if value not in res1]
                        ans2 = ans + list(set(res1) - set(ans))
                        print(sorted(ans2))
                        ans = ans2
                        break

        i += 1
    return ans


# this function validates the existence of files containing inverted index and positional index,if they exist it reads and loads the indexes from file,else creates both indexes and saves them in separate files
filereader()

# GUI


def checkQueryType():
    query = inputBox.get()
    print(query[len(query) - 2][0])
    if query[len(query) - 2][0] == '/':  # process proximity query if presence of '/' is there
        result = processPQuery(query)
        result_box.delete(0.0, 'end')
        result_box.insert('end', sorted(set(result)))
    else:
        result = processQeury(query)
        result_box.delete(0.0, 'end')
        result_box.insert('end', sorted(set(result)))


root = tk.Tk()
root.geometry("700x500")
root['bg'] = 'black'
root.title('Boolean Retreival Model')
tk.Label(root, text="Boolean Retreival Model",
         font=("Roboto", 20)).pack(pady=(5, 10))
tk.Label(root, text="Type Your Query Below",
         font=("Roboto", 12)).pack(pady=(10, 2))
inputBox = tk.Entry(root, font=("Roboto", 12), width=45)
inputBox.pack()
submitButton = tk.Button(root, text="SUBMIT", width=40,
                         command=checkQueryType).pack()
tk.Label(root, text="Result-set", font=("Roboto", 12)).pack(pady=(10, 2))
root.bind('<Return>', checkQueryType)
result_box = tk.Text(root, width=50, height=20,
                     font=("Roboto", 12), wrap='word', fg='red')

result_box.pack(pady=(2, 10),)

root.mainloop()
