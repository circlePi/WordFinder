"""
不依赖词典(基于统计)的抽词算法-新词发现算法基础
Author: zelindai
Date:   2019/07/31
ref：https://www.matrix67.com/blog/archives/5044
"""
import math
from collections import Counter
from tqdm import tqdm


# 设置阈值
## 频数
freq_threshold = 20
## 最大长度
max_len = 5
## 凝固程度
integrity_threshold = 100
## 互信息 (自由成词程度)
entropy_threshold = 3


def get_all_possible_substring(s, max_len):
    print("提取所有可能的子串...")
    sub = {}
    N = len(s)
    for i in range(1, max_len+1):
        start, end = 0, 0
        while end < N:
            token = s[start: start + i]
            if start != 0:
                left_word = s[start - 1]
            else:
                left_word = -1
            if end != N - 1:
                right_word = s[start + i]
            else:
                right_word = -1

            if sub.get(token) is None:
                sub[token] = {"left": [left_word], "right": [right_word], "freq": 1}
            else:
                sub[token]["left"].append(left_word)
                sub[token]["right"].append(right_word)
                sub[token]["freq"] += 1
            start += 1
            end = start + i
        i += 1
    # print(sub["林黛玉"])
    return sub


def count(neighbor):
    N_left = len(neighbor)
    l_count = Counter(neighbor)
    l_count = [v / N_left for _, v in l_count.items()]
    return l_count


def compute_entropy(s):
    """计算互信息（自由度）"""
    left = [l for l in s["left"] if l != -1]
    right = [r for r in s["right"] if r != -1]
    l_count = count(left)
    r_count  =count(right)
    l_entropy = sum([-l * math.log(l) for l in l_count])
    r_entropy = sum([-r * math.log(r) for r in r_count])
    return (l_entropy + r_entropy) / 2


def enumerate_all_possible_combination(token):
    candidates = []
    N = len(token)
    p = 1
    while p < N:
        candidates.append((token[:p], token[p:]))
        p += 1
    return candidates


def compute_integrity(sub, token):
    """计算凝固度"""
    candidates = enumerate_all_possible_combination(token)
    token_freq = sub[token]["freq"]
    integrity = []

    for c in candidates:
        integrity.append(token_freq / (sub[c[0]]["freq"]) * sub[c[1]]["freq"])
    integrity = sorted(integrity)
    return integrity[0]


def read_text(text_path, stop_word_list=None):
    """将文本读成一个字符串"""
    with open(text_path, 'r') as fr:
        text = fr.read()
    if stop_word_list is not None:
        for w in stop_word_list:
            text = text.replace(w, "")
    return text


def main(text_path, stop_word_list=None):
    result = []
    text = read_text(text_path, stop_word_list)
    sub = get_all_possible_substring(text, max_len)
    all_tokens = list(sub.keys())
    print("开始抽取满足阈值的词...")
    for t in tqdm(all_tokens):
        if sub[t]["freq"] < freq_threshold:
            continue
        s_entropy = compute_entropy(sub[t])
        if len(t) > 1:
            s_integrity = compute_integrity(sub, t)
        else:
            s_integrity = 0
        if (s_entropy > entropy_threshold) and (s_integrity > integrity_threshold):
            result.append((t, sub[t]["freq"]))
    result = sorted(result, key=lambda x:x[1], reverse=True)
    with open("./word_found_result.txt", 'w') as fw:
        for r in result:
            token = r[0]
            if len(token) > 1:
                fw.write(token+"\t"+str(r[1])+"\n")
    print("抽取完成!")


if __name__ == "__main__":
    stop_word_list = [".", "。", "，", "？", "”", "．", "：", "“", "！", "'`", "\"", "\'", ",", "*", "\n", "\t", "了"," ", "的", "呢", "\u3000"]
    main(text_path="hongloumeng.txt", stop_word_list=stop_word_list)
