
import os
import nltk
import pandas as pd
from wordcloud import WordCloud
from cutecharts.charts import Pie
from cutecharts.charts import Bar
from cutecharts.charts import Line
from cutecharts.charts import Radar
from nltk.sentiment.vader import SentimentIntensityAnalyzer


'''check dir'''


def checkDir(dirpath):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
        return False
    return True


'''读取csv文件'''


def readCSV(filepath='twitters.csv'):
    data = pd.read_csv(filepath, lineterminator='\n')
    data['time'] = pd.to_datetime(data['created_at']).dt.tz_convert(
        'US/Eastern').dt.strftime('%Y/%m/%d %H:%M:%S')
    data['time'] = pd.to_datetime(data['time'])
    return data


'''折线图'''


def drawLine(title, data, series_name, x_label, y_label, savedir='results'):
    checkDir(savedir)
    chart = Line(title)
    chart.set_options(
        labels=list(data.keys()),
        x_label=x_label,
        y_label=y_label
    )
    chart.add_series(series_name, list(data.values()))
    chart.render(os.path.join(savedir, title+'.html'))


'''柱状图'''


def drawBar(title, data, series_name, x_label, y_label, savedir='results'):
    checkDir(savedir)
    chart = Bar(title)
    chart.set_options(
        labels=list(data.keys()),
        x_label=x_label,
        y_label=y_label
    )
    chart.add_series(series_name, list(data.values()))
    chart.render(os.path.join(savedir, title+'.html'))


'''画饼图'''


def drawPie(title, data, savedir='results'):
    checkDir(savedir)
    chart = Pie(title)
    chart.set_options(labels=list(data.keys()))
    chart.add_series(list(data.values()))
    chart.render(os.path.join(savedir, title+'.html'))


'''雷达图'''


def drawRadar(title, datas, series_names, savedir='results'):
    checkDir(savedir)
    chart = Radar(title)
    chart.set_options(labels=list(datas[0].keys()))
    for data, series_name in zip(datas, series_names):
        chart.add_series(series_name, list(data.values()))
    chart.render(os.path.join(savedir, title+'.html'))


'''统计词频'''


def statisticsWF(texts, stopwords):
    words_dict = {}
    for text in texts:
        words = text.split(' ')
        for word in words:
            word = word.lower().replace('[', '').replace(
                ']', '').replace('.', '').replace(',', '')
            if word in stopwords:
                continue
            if word in words_dict.keys():
                words_dict[word] += 1
            else:
                words_dict[word] = 1
    return words_dict


'''词云'''


def drawWordCloud(words, title, savedir='results'):
    checkDir(savedir)
    wc = WordCloud(font_path='font.TTF', background_color='white',
                   max_words=2000, width=1920, height=1080, margin=5)
    wc.generate_from_frequencies(words)
    wc.to_file(os.path.join(savedir, title+'.png'))


'''run'''
if __name__ == '__main__':
    # 数据读取
    twitters = readCSV('twitters.csv')
    # 特朗普每年发的推特数量

    num_twitters_per_year = {}
    for item in twitters['time']:
        if item.year in num_twitters_per_year:
            num_twitters_per_year[item.year] += 1
        else:
            num_twitters_per_year[item.year] = 1
    num_twitters_per_year = dict(
        sorted(num_twitters_per_year.items(), key=lambda item: item[0]))
    print(num_twitters_per_year)
    drawLine('特朗普每年发的推特数量', num_twitters_per_year,
             '推特数量', x_label='年份', y_label='数量')

    # 特朗普用哪些设备发推特
    '''
    num_twitters_per_device = {}
    for item in twitters['source']:
        item = item.replace('Twitter for ', '').replace('Twitter ', '').replace('Twitter Mirror for ', '')
        if item in num_twitters_per_device:
            num_twitters_per_device[item] += 1
        else:
            num_twitters_per_device[item] = 1
    num_twitters_per_device = dict(sorted(num_twitters_per_device.items(), key=lambda item: item[1])[-5:])
    drawBar('特朗普都用哪些设备发推特', num_twitters_per_device, '设备类型', x_label='设备类型', y_label='数量')
    '''
    # 特朗普发推特的时间统计
    '''
    num_twitters_per_period = {}
    for item in twitters['time']:
        if item.hour in num_twitters_per_period:
            num_twitters_per_period[item.hour] += 1
        else:
            num_twitters_per_period[item.hour] = 1
    num_twitters_per_period = dict(sorted(num_twitters_per_period.items(), key=lambda item: item[0]))
    drawLine('特朗普发推特的时间统计', num_twitters_per_period, '推特数量', x_label='时间', y_label='数量')
    '''
    # 特朗普上任后每年提到奥巴马的次数
    '''
    num_obama_per_year = {}
    for item in zip(twitters['time'], twitters['text']):
        if item[0].year in num_obama_per_year:
            num_obama_per_year[item[0].year] += int('obama' in item[1].lower())
        else:
            num_obama_per_year[item[0].year] = int('obama' in item[1].lower())
    num_obama_per_year = dict(sorted(num_obama_per_year.items(), key=lambda item: item[0])[-3:])
    drawPie('特朗普上任后每年提到奥巴马的次数', num_obama_per_year)
    '''
    # 特朗普奥巴马相关的推特情绪分析
    '''
    nltk.download('vader_lexicon')
    sid = SentimentIntensityAnalyzer()
    neg_or_pos_for_obama = {'pos': 0, 'neg': 0, 'neu': 0}
    for item in twitters['text']:
        if 'obama' in item.lower():
            score = sid.polarity_scores(item)
            score.update({'compound': -1e5})
            neg_or_pos_for_obama[max(score, key=score.get)] += 1
    drawPie('特朗普奥巴马相关的推特情绪分析', neg_or_pos_for_obama)
    '''
    # 特朗普提到最多的美国媒体
    '''
    num_twitters_per_media = {}
    medias = ['fortune magazine', 'national review', 'politico', 'los angeles times', 'guardian', 'usa today',
              'new hampshire union leader', 'esquire magazine', 'cnet', 'gq magazine', 'weekly standard', 'hbo', 
              'tmz', 'npr', 'los angeles daily', 'bloomberg', 'the view', 'univision', 'newsweek', 'wall street journal',
              'techmeme', 'huffington post', 'meet the press', 'cnn', 'fox', 'national journal', 'msnbc', 'bbc', 'buzzfeed',
              'cnbc', 'des moines register ', 'time magazine', 'vanity fair', 'ny mag', 'cbs', 'ny post', 'ny daily', "o'reilly factor",
              'espn', 'charlie hebdo', 'associated press', 'morning joe', 'deadspin', 'time magazine ', 'washington post', 'palm beach post',
              'rolling stone', 'nbc', 'new york times', 'abc', 'huffpost']
    for media in medias: num_twitters_per_media[media] = 0
    for item in twitters['text']:
        for media in medias:
            if media in item.lower():
                num_twitters_per_media[media] += 1
    num_twitters_per_media = dict(sorted(num_twitters_per_media.items(), key=lambda item: item[1])[-6:])
    drawBar('特朗普提到最多的六大美国媒体', num_twitters_per_media, '媒体', x_label='媒体', y_label='数量')
    '''
    # 特朗普FOX/NBC/CNN相关的推特情绪分析
    '''
    sid = SentimentIntensityAnalyzer()
    neg_or_pos_for_fox = {'pos': 0, 'neg': 0, 'neu': 0}
    neg_or_pos_for_nbc = {'pos': 0, 'neg': 0, 'neu': 0}
    neg_or_pos_for_cnn = {'pos': 0, 'neg': 0, 'neu': 0}
    for item in twitters['text']:
        if 'fox' in item.lower():
            score = sid.polarity_scores(item)
            flag = True
            if score['neg'] > 0.1:
                neg_or_pos_for_fox['neg'] += 1
                flag = False
            if score['pos'] > 0.2:
                neg_or_pos_for_fox['pos'] += 1
                flag = False
            if flag:
                score.update({'compound': -1e5})
                neg_or_pos_for_fox[max(score, key=score.get)] += 1
        if 'nbc' in item.lower():
            score = sid.polarity_scores(item)
            flag = True
            if score['neg'] > 0.1:
                neg_or_pos_for_nbc['neg'] += 1
                flag = False
            if score['pos'] > 0.2:
                neg_or_pos_for_nbc['pos'] += 1
                flag = False
            if flag:
                score.update({'compound': -1e5})
                neg_or_pos_for_nbc[max(score, key=score.get)] += 1
        if 'cnn' in item.lower():
            score = sid.polarity_scores(item)
            flag = True
            if score['neg'] > 0.1:
                neg_or_pos_for_cnn['neg'] += 1
                flag = False
            if score['pos'] > 0.2:
                neg_or_pos_for_cnn['pos'] += 1
                flag = False
            if flag:
                score.update({'compound': -1e5})
                neg_or_pos_for_cnn[max(score, key=score.get)] += 1
    drawRadar('特朗普FOX_NBC_CNN相关的推特情绪分析', [neg_or_pos_for_fox, neg_or_pos_for_nbc, neg_or_pos_for_cnn], ['fox', 'nbc', 'cnn'])
    '''
    # 特朗普所有推特词云
    stopwords = open('enstopwords.data', 'r',
                     encoding='utf-8').read().split('\n')
    texts = [item for item in twitters['text']]
    words_dict = statisticsWF(texts, stopwords)
    drawWordCloud(words_dict, '特朗普推特词云')
