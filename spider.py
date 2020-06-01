# -*- coding:utf-8 -*-
############# bilibili弹幕抓取
############# by k 2020/5/6
import requests
import re
from bs4 import BeautifulSoup
import operator  # 排序


def getHTMLText(url):
    try:
        # print("获取url中...")
        r = requests.get(url, timeout=30)
        r.raise_for_status()  # 判断网络连接的状态
        r.encoding = r.apparent_encoding
        # r.encoding：从HTTP的header中猜测的编码；
        # r.apparent_encoding： 从内容中分析的编码（备选编码方式）
        # print("获取url完成")
        return r.text  # 输出文本信息内容
    except:
        print("获取Url失败")


def parsePage(text):
    try:
        # print("解析文本...")
        keyStr = re.findall(r'"cid":[\d]*', text)  # B站有两种寻址方式，第二种多一些
        if not keyStr:  # 若列表为空，则等于“False”
            keyStr = re.findall(r'cid=[\d]*', text)
            key = eval(keyStr[0].split('=')[1])
        else:
            key = eval(keyStr[0].split(':')[1])  # 获取弹幕储存地址关键字
        commentUrl = 'https://comment.bilibili.com/' + str(key) + '.xml'  # 弹幕存储地址
        # print("弹幕解析")
        commentText = getHTMLText(commentUrl)
        soup = BeautifulSoup(commentText, "html.parser")
        soup2 = BeautifulSoup(text, "html.parser")
        commentList = {}
        title = soup2.find('h1').get_text().strip()  # find()方法，获取文本，去掉空格
        for comment in soup.find_all('d'):
            time = float(comment.attrs['p'].split(',')[0])  # tag.attrs（标签属性，字典类型）
            commentList[time] = comment.string
        newDict = sorted(commentList.items(), key=operator.itemgetter(0))  # 字典排序
        commentList = dict(newDict)
        # print("解析文本完成")
        return commentList, title
    except:
        print("解析失败")


def float2time(f):
    timePlus = int(f)
    m = timePlus // 60
    s = timePlus - m * 60
    return str(m) + ':' + str(s).zfill(2)


def ioFunc(commentList, title, root):
    # print("写入文本中...")
    path = root + "\\" + title + '.txt'
    # print(path)
    f = open(path, 'w', encoding='utf-8')  # windows默认gbk编码输出，与网络编码“utf-8”不符
    begin = "{}\n共有{}条弹幕\n".format(title, len(commentList))
    f.write(begin)
    ws = "{:7}\t{}\n".format('time', 'comment')
    f.write(ws)
    lastTime = 0
    for time, string in commentList.items():  # 记得items()
        lastTime = float2time(time)
        ws = "{:7}\t{}\n".format(lastTime, string)
        f.write(ws)  # 手动换行
    f.close()


import requests
from lxml import etree


# 简单破解反爬虫机制，使用headers模拟浏览器
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                 'Chrome/81.0.4044.129 Safari/537.36'
}


# 得到指定搜索页面上所有的链接信息，以供搜索招聘的具体信息
def get_link(key_word, page):
    url = 'https://search.bilibili.com/all?keyword=' + key_word + '&page=' + str(page)
    html = requests.get(url, headers=headers)
    html_xpath = etree.HTML(html.text)  # 获取网页中的所有信息并转化成xpath
    link_all = html_xpath.xpath('//*[@id="all-list"]/div[1]/ul/li/a/@href')
    return link_all


if __name__ == '__main__':
    # 批量视频爬取
    key_word = '疫情'
    page_all = 50
    for page in range(2, page_all):
        print('正在爬取第{}页链接信息'.format(page))
        try:
            link_all = get_link(key_word, page)
            for link in link_all:
                # 爬取弹幕信息
                root = r"data"
                link = 'https:' + link
                text = getHTMLText(link)
                commentList, title = parsePage(text)
                ioFunc(commentList, title, root)
        except:
            print('第{}页链接信息爬取失败'.format(page))
            continue
    # 单独视频弹幕爬取
    # av = input('Put in av number: ')  # 视频地址
    # url = r"https://www.bilibili.com/video/av" + str(av)
    # root = r"data"
    # url = r"https://www.bilibili.com/video/BV12p4y1973P"
    # text = getHTMLText(url)
    # commentList, title = parsePage(text)
    # # title = av + title
    # ioFunc(commentList, title, root)
    # print("Finish.")


