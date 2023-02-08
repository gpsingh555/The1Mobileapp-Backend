from newsapi import NewsApiClient
from datetime import datetime, timedelta, date
from .models import *


def upload_news():
    print("Started  pulling news ....")
    for keyword in list(news_keyword.objects.all().values_list("keyword", flat=True)):
        print(f"started getting news for keyword => {keyword}")
        newsapi = NewsApiClient(api_key='3b80f2716a74411eaeab937b44871cebn')
        all_articles = newsapi.get_everything(q=keyword,
                                              from_param=str(date.today() - timedelta(1)),
                                              to=str(date.today() - timedelta(1)),
                                              language='en',
                                              sort_by='relevancy',
                                              page_size=50)

        try:
            total_page = all_articles['totalResults'] // 20
        except:
            total_page = 1
        print(total_page, '------------total page')
        # for page in range(1,total_page+1):
        #     articles = newsapi.get_everything(q=keyword,
        #                                           from_param=str(date.today() - timedelta(1)),
        #                                           to=str(date.today() - timedelta(1)),
        #                                           language='en',
        #                                           sort_by='relevancy',
        #                                           page=page)
        for x in all_articles['articles']:
            print(x['title'])
            print(x['author'])
            print(x['title'])
            print(x['content'])
            print(x['urlToImage'])
            print(x['description'])
            print(x['url'])
            print(datetime.strptime(
                x['publishedAt'].split("T")[0] + " " + x['publishedAt'].split("T")[-1].replace("Z", ""),
                "%Y-%m-%d %H:%M:%S"))

            if News.objects.filter(title=x['title']).exists() == False:
                print("Enter")
                ews = News.objects.create(title=x['title'])
                if x['author'] != None:
                    ews.author = x['author']
                ews.user = User.objects.filter(is_superuser=True).first()
                ews.title = x['title']
                ews.description = x['description']
                ews.publishedAt = datetime.strptime(
                    x['publishedAt'].split("T")[0] + " " + x['publishedAt'].split("T")[-1].replace("Z", ""),
                    "%Y-%m-%d %H:%M:%S")
                ews.content = x['content']
                ews.urlToImage = x['urlToImage']
                ews.url = x['url']
                ews.keyword = keyword
                ews.save()

    # sources = newsapi.get_sources()
    # print(sources)
