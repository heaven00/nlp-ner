import os, time
from json import load
from jsonrpclib import Server
from simplejson import loads
from multiprocessing import Pool

def is_file(file_path):
    """
    Checks whether the file exists or not and is valid.
    """
    if os.path.exists(file_path):
        if os.path.isfile(file_path):
            return True
        else:
            raise IOError('The path does not point to a valid file.')
    else:
        raise IOError('The file does not Exist')
    
def get_data(file_path):
    """
    Get the articles from the give file path.
    """
    if is_file(file_path):
        f = open(file_path)
        data = load(f)
    return data
    
def chunks(data, n):
    """
    divide the list of data into n equal parts
    """
    return [data[i:i+n] for i in xrange(0, len(data), n)]

def nlp_parse(text):
    """
    pass the text to the stanford NLP core server and get the parsed data
    """
    server = Server("http://localhost:8080")
    parsed_data = loads(server.parse(text))
    return parsed_data

def nlp_parse_multi(split_article):
    """
    Parse each sentence of the article separately.
    """
    server = Server("http://localhost:8080")
    re = []
    for sentence in split_article:
        result = loads(server.parse(sentence))
        re.append(result)
    return re
    
def get_NER_list(data):
    """
    Take the parsed article as input and extract the NER for each word.
    """
    entity_word_list = []
    for data in data['sentences']:
        for word_data in data['words']:
            word = word_data[0]
            NER = word_data[1]['NamedEntityTag']
            if NER != 'O' and word not in entity_word_list:
                entity_word_list.append(word)
    return entity_word_list
#
#def get_bulk_NER_list(data):
#    """
#    A trial with multiProcesses.
#    """
#    entity_word_list = []
#    for data_item in data:
#        for sentence in data_item['sentences']:
#            for word_data in sentence['words']:
#                word = word_data[0]
#                NER = word_data[1]['NamedEntityTag']
#                if NER != 'O':
#                    entity_word_list.append(word)
#    return entity_word_list

def get_multi_NER_list(data):
    entity_word_list = []
    for item in data:
        for sentence in item['sentences']:
            for word_data in sentence['words']:
                word = word_data[0]
                NER = word_data[1]['NamedEntityTag']
                if NER != 'O' and word not in entity_word_list:
                    entity_word_list.append(word)
    return entity_word_list
    
def main(articles, thread_id=1):
    """
    The main.
    Go through the list of articles and parse it using the nlp_parse() function.
    """
    f = open('resources/log/test.log','w+')
    for i in xrange(800, len(articles)):
        if i not in [280]:
            T1 = time.time()
            article = articles[i]['description']
            if len(article) <= 4000:
                result = nlp_parse(article)
                entity_list = get_NER_list(result)            
            else:
                article_sentences = article.split('.')
                result = nlp_parse_multi(article_sentences)
                entity_list = get_multi_NER_list(result)
            T2 = time.time()
            NER_count = len(entity_list)
            NER_words = entity_list
            elapsed_time = T2-T1
            article_id = i
            log = "Article ID: {0}, Elapsed Time: {1},ThreadID:{4}, Number of NER's: {2}, NER: {3}".format(article_id, \
                                                                        elapsed_time, NER_count, NER_words, thread_id)
            f.write(log)
            f.write('\n')
            print i
    f.close()

data = get_data('resources/data/article_dump.json')
main(data)
#!WRTIE IPYTHON CODE TO RUN THIS ON MULTIPLE PROCESSES.