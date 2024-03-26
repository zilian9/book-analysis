import time
from collections import Counter
import jieba
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Book
import numpy as np
from django.db.models import Count

from django.shortcuts import render
from pyecharts.charts import Line
from .models import Comment  # 假设你有一个Comment模型，用于存储评论数据
from django.shortcuts import render
from django.http import JsonResponse
import json

from django.shortcuts import render
from pyecharts import options as opts
from pyecharts.charts import WordCloud
from pyecharts.globals import SymbolType

def word_cloud(request):
    filepath='/Users/k/project/Book_Analysis/O2FmEjpUU_word.txt'
    word_count = {}
    fp = open(filepath,'r',encoding='utf8')
    for line in fp:
        new_line=[]
        if len(line)>1:
            line = line.strip().split(' ')
            for word in line:
                if word in word_count:
                    word_count[word] += 1
                else:
                    word_count[word] = 1

    del word_count['spanclass']
    del word_count['url']
    del word_count['icon']
    words = [(word, count) for word, count in word_count.items()]
    # 构造词云图数据
    # words = [
    #     ("Python", 10000),
    #     ("Django", 6181),
    #     ("Flask", 4386),
    #     ("Java", 4055),
    #     ("C++", 2467),
    #     ("JavaScript", 2244),
    #     # 其他词语...
    # ]

    # 绘制词云图
    c = (
        WordCloud()
        .add("", words, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
        .set_global_opts(title_opts=opts.TitleOpts(title="词云图示例"))
    )

    # 将图表转换为 HTML 字符串
    word_cloud_html = c.render_embed()

    return render(request, 'system/word_cloud.html', {'word_cloud_html': word_cloud_html})


def average_sentiment(request):
    # 获取评论数据
    comments = Comment.objects.all()

    # 计算每天评论情感概率的平均值
    date_sentiment_avg = {}
    for comment in comments:
        date = comment.date
        sentiment = comment.probability
        if date in date_sentiment_avg:
            date_sentiment_avg[date].append(sentiment)
        else:
            date_sentiment_avg[date] = [sentiment]

    date_avg = []
    sentiment_avg = []
    for date, sentiment_list in date_sentiment_avg.items():
        avg = sum(sentiment_list) / len(sentiment_list)
        date_avg.append(date.strftime('%Y-%m-%d'))
        sentiment_avg.append(avg)

    # 将数据转换为 JSON 格式
    data = {'dates': date_avg, 'sentiments': sentiment_avg}
    return render(request, 'system/sentiment_avg_line_chart.html', {'data': json.dumps(data)})

    return render(request, 'system/sentiment_avg_line_chart.html')


from django.shortcuts import render
from pyecharts import options as opts
from pyecharts.charts import Pie
from collections import Counter

def pie_chart(request):
    # 统计 polarity 字段中不同值的数量
    comments = Comment.objects.all()
    polarity_counts = Counter(comment.polarity for comment in comments)

    # 获取极性值和数量
    polarities = list(polarity_counts.keys())
    counts = list(polarity_counts.values())
    # 创建一个饼图
    c = (
        Pie()
        .add("", [list(z) for z in zip(polarities, counts)])
        .set_global_opts(title_opts=opts.TitleOpts(title="评论情感倾向分布饼图"))
    )
    # 将饼图转换为HTML格式的字符串
    pie_html = c.render_embed()
    return render(request, 'system/chart_pie.html', {'pie_html': pie_html})


from django.shortcuts import render
from .models import Comment

def comment_list(request):
    comments = Comment.objects.all()
    return render(request, 'system/comment_list.html', {'comments': comments})


@login_required(login_url='/login/')
def index(request):
    return render(request, 'system/index.html')

@login_required(login_url='/login/')
def show(request):
    books = Book.objects.all()
    date = time.strftime("%Y-%m-%d", time.localtime())
    count_today = len(books.filter(addTime__gt=date))
    count_sum = len(books)
    return render(request, 'system/show.html',context={'count_today':count_today,'count_sum':count_sum})

@login_required(login_url='/login/')
def chart1(request):
    category = request.GET.get('category')
    categories = Book.objects.order_by('category').values('category').distinct()
    data = {}
    if category:
        prices = list(Book.objects.all().filter(category=category).values_list('now_price', flat=True))
        bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, np.inf]
        bin_names = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90-100', '100+']
        # 将价格分组
        counts, bins = np.histogram(prices, bins=bins)
        # 构造返回结果
        # x_data = [str(bins[i]) + '-' + str(bins[i + 1]) for i in range(len(bins) - 1)]
        y_data = counts.tolist()

        data['x_data'] = bin_names
        data['y_data'] = y_data

    return render(request, 'system/chart1.html', context={'categories':categories,'data':data,'category':category})

@login_required(login_url='/login/')
def chart2(request):
    category = request.GET.get('category')
    categories = Book.objects.order_by('category').values('category').distinct()
    data = {}
    if category:
        publishers = Book.objects.all().filter(category=category).values('press').annotate(count=Count('id')).order_by('-count')
        data['x_data'] = []
        data['y_data'] = []
        for item in publishers[:5]:
            data['x_data'].append(item['press'])
            data['y_data'].append({'name':item['press'],'value':item['count']})
    return render(request, 'system/chart2.html', context={'categories':categories,'category':category,'data':data})


@login_required(login_url='/login/')
def recommend(request):
    books = Book.objects.all().order_by('-comment_num')
    paginator = Paginator(books, 18)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    return render(request, 'system/recommend.html',context={'books':books,'page':page})

def get_echart_data(request):
    returnData = {'echart_1':{},'echart_2':{},'echart_3':{},'echart_4':{},'echart_5':{},'echart_6':{}}
    books = Book.objects.all()

    # echart_1
    category_results = books.values('category').annotate(count=Count('id'))
    returnData['echart_1']['x_data'] = [item['category'] for item in list(category_results)]
    returnData['echart_1']['y_data'] = [item['count'] for item in list(category_results)]

    # echart_2
    prices_results = list(books.values_list('now_price', flat=True))
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, np.inf]
    bin_names = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90-100', '100+']
    # 将价格分组
    counts, bins = np.histogram(prices_results, bins=bins)
    # 构造返回结果
    returnData['echart_2']['x_data'] = bin_names
    returnData['echart_2']['y_data'] = counts.tolist()

    # echart_3
    detail_results = books.filter(star__gt=90).values('detail')
    content = ""
    for result in detail_results:
        content += result['detail']
    stopwords = set()
    with open('./system/cn_stopword.txt', 'r', encoding='utf-8') as fp:
        for line in fp:
            stopwords.add(line.strip())
    content = jieba.lcut(content, cut_all=False)
    filtered_words = []
    for word in content:
        if word not in stopwords:
            filtered_words.append(word)
    content = filtered_words
    word_counts = Counter(content)  # 对分词做词频统计
    word_counts_top = word_counts.most_common(100)
    returnData['echart_3']['data'] = []
    for key, value in word_counts_top:
        returnData['echart_3']['data'].append({'name': key, 'value': value})

    # echart_4
    publishers = books.values('press').annotate(count=Count('id')).order_by('-count')
    returnData['echart_4']['data'] = [{'name':item['press'],'value':item['count']} for item in publishers[:10]]

    # echart_5
    star_results = books.values('star').annotate(count=Count('id')).order_by('star')
    returnData['echart_5']['x_data'] = [item['star'] for item in list(star_results)]
    returnData['echart_5']['y_data'] = [item['count'] for item in list(star_results)]

    # echart_6
    comment_results = books.values('title','comment_num').order_by('-comment_num')[:5]
    returnData['echart_6']['x_data'] = [item['title'] for item in list(comment_results)]
    returnData['echart_6']['y_data'] = [{'name':item['title'],'value':round(item['comment_num']/10000,2)} for item in list(comment_results)]
    return JsonResponse(returnData,safe=False, json_dumps_params={'ensure_ascii': False})
