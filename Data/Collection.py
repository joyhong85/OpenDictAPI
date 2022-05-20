import urllib3
import json
import pandas as pd
import os
from numpy import random
from time import sleep
from tqdm import tqdm
from datetime import datetime


def get_dict_from_opendict(key_no):
    """
    우리말샘 API에서 json 결과를 가져온다.
    :param key_no:  api_count.txt 에서 획득한 순차적 번호
    :return:
    """
    url = opendict_api + str(key_no)
    http = urllib3.PoolManager()
    response = http.request('GET', url)

    try:
        json_data = json.loads(str(response.data, "utf-8"))
    except:
        return None

    return json_data


def refine_label(word):
    """
    - : 최소 분할 단위
    ^ : 띄어쓰는 것이 원칙이나 붙여 쓸 수 있다는 표시
    이러한 구분자를 제거 혹은 공백으로 변환
    :param word:
    :return:
    """
    refined_set = {word}
    refined_set.add(word.replace('-', ''))
    refined_set.add(word.replace('^', ' '))
    refined_set.add(word.replace('^', ''))
    return list(refined_set)


def make_data(json_data):
    """
    JSON 데이터로부터 필요한 정보를 추출
    :param json_data:
    :return:
    """
    original_url = json_data['channel']['link']  # 원문 URL
    identifier = original_url[original_url.rfind('=') + 1:]  # 내부 식별 번호
    wordInfo = json_data['channel']['item']['wordInfo']  # 단어에 대한 정보 컨테이너
    word = wordInfo['word']  # 단어
    word_unit = wordInfo['word_unit']  # 구성 단위
    word_type = wordInfo['word_type']  # 고유어 구분
    original_language_info = wordInfo['original_language_info'] \
        if 'original_language_info' in wordInfo.keys() else ''  # 원어

    refined_word = refine_label(word)  # 단어 표기를 정제

    senseInfo = json_data['channel']['item']['senseInfo']  # 의미정보 컨테이너
    definition = senseInfo['definition']  # 단어 뜻
    sense_no = senseInfo['sense_no']  # 단어 어깨번호
    category = senseInfo['type']  #
    pos = senseInfo['pos'] if 'pos' in senseInfo.keys() else ''  # 품사 구분
    relationInfo = senseInfo['relation_info'] if 'relation_info' in senseInfo.keys() else ''  # 연관정보 컨테이너
    translationInfo = senseInfo['translation_info'] \
        if 'translation_info' in senseInfo.keys() else ''  # 대역어 컨테이너
    main_domain = ",".join(senseInfo['cat_info'] if 'cat_info' in senseInfo.keys() else '')  # 전문 분야
    proverbInfo = senseInfo['proverb_info'] if 'proverb_info' in senseInfo.keys() else ''  # 관용구 / 속담 컨테이너
    title = word + str(sense_no)  # 단어와 어깨번호로 타이틀 생성

    original_word = ''  # 원어 단어
    origin_language_type_list = []
    for langinfo in original_language_info:
        original_language = langinfo['original_language'].strip()
        origin_language_type = langinfo['language_type'].strip()
        origin_language_type_list.append(origin_language_type)
        original_word += original_language

    translation = ''  # 대역어
    translation_language_type = ''
    for transinfo in translationInfo:
        translation = transinfo['translation'].strip()
        translation_language_type = transinfo['language_type'].strip()

    original_word_type = origin_language_type_list[0] if len(origin_language_type_list) == 1 else ''  # 원어 단어 타입

    __result = [identifier, word, title, "|".join(refined_word), word_unit, word_type, pos, sense_no, category,
                definition, main_domain, original_url, translation, translation_language_type,
                original_word, original_word_type]

    __relationship = []
    for relInfo in relationInfo:
        __relationship.append([identifier, relInfo['link_target_code'], relInfo['type'], relInfo['word']])
    for proInfo in proverbInfo:
        __relationship.append([identifier, proInfo['link_target_code'], proInfo['type'], proInfo['word']])

    return __result, __relationship


def get_start_no():
    """
    실행시 시작 번호를 획득한다.
    :return:
    """
    f = open(count_file, 'r')
    line = f.readline()
    __last_no: int = int(line)
    f.close()

    return __last_no


def check_last_no():
    """
    최신 번호를 파일에 저장
    :return:
    """
    f = open(count_file, 'w')
    f.write(str(last_no))
    f.close()


def check_point():
    """
    현재 결과를 저장한다.
    :return:
    """
    global df_rel
    global isFirst
    check_last_no()
    if isFirst:
        df_word.to_csv(seed_file_name)
    else:
        df_word.to_csv(seed_file_name, mode='a', header=False)
    isFirst = False

    df_rel.to_csv(rel_file_name, mode='a', header=False)
    df_rel = pd.DataFrame()


def check_api_key(q_no):
    json_data = get_dict_from_opendict(q_no)
    if json_data:
        return True
    return False


if __name__ == '__main__':
    api_key = input("Input API Key for OpenDict Collection: ")

    opendict_api = 'http://opendict.korean.go.kr/api/view?certkey_no=3902&key=' + api_key + '&target_type=view&req_type=json&method=target_code&q='

    if not check_api_key(1):
        print("API Key is not correct..Check your key")
        exit()

    path = os.getcwd()
    count_file = path + "/api_count.txt"

    datestr = datetime.today().strftime("%Y%m%d")
    seed_file_name = path + "/result/word_seed_" + datestr + ".csv"
    rel_file_name = path + "/result/word_relation_" + datestr + ".csv"

    isFirst = False
    if not os.path.isfile(seed_file_name):
        isFirst = True

    df_index = ['identifier', 'word', 'main_title', 'label', 'word_unit', 'word_type', 'pos', 'sense_no', 'category',
                'definition', 'main_domain', 'original_url', 'translation', 'translation_language_type',
                'original_word',
                'original_word_type']

    df_word = pd.DataFrame(columns=df_index)
    df_rel = pd.DataFrame()

    sleeptime = random.uniform(0.4, 1)

    last_no = get_start_no()

    print("Start No :: " + str(last_no))

    for i in tqdm(range(0, 10), position=0, leave=True):
        try:
            last_no += 1
            json_data = get_dict_from_opendict(last_no)
            if json_data:
                result, relationship = make_data(json_data)
                df_rel = pd.concat([df_rel, pd.DataFrame(relationship)])
                if df_word[-1:].empty:
                    df_word.loc[0] = result
                else:
                    df_word.loc[df_word[-1:].index[0] + 1] = result

        except:
            last_no = last_no - 1
            print("error occured..")
            print("last_no is " + str(last_no))

            check_point()
            break

        if last_no % 100 == 0:
            check_point()

    #     sleep(sleeptime)

    check_point()
