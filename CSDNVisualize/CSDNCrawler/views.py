from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.http import HttpResponse, Http404
from django.http import JsonResponse

from libCrawler.PersonalData import *
from libCrawler.PersonalData.webpage import UserData
from libCrawler.PersonalData.blogpage import PersonBlogCSDN, PersonalArticles
from libCrawler.PersonalData.webpage import SocialData
from libCrawler.PersonalData.exceptions import *

import sys
# import os
from django.template import loader
from .models import UserID, VisualData
from .models import Article
from datetime import datetime
import re
import json

import shelve
from collections import OrderedDict, ChainMap

doDebug = True

"""CSDN-Data configuration
Crawler part configuration:
    "no-head browser path": /opt/phantomjs/bin/phantomjs

    "follows user id db path": /mnt/sandi_TF/Plateform/database/follows_shelve/
Other part configuration reserve.
"""


def save_all_follows_of_new_userid_to_shelve(user_id, db_path):
    """ !! 使用 shelve 的方式，如果 db 在另外的进程中打开，
    保存数据进去将会有问题！！
    问题推测更加具体一点应该是同一个 shelve[key] 会保存最后那个进程保存的。
    """
    csdn_userid_socialData = personalProfile.SocialData(
        user_id, browser_path='/opt/phantomjs/bin/phantomjs')
    follows = csdn_userid_socialData.getFollows()
    try:
        if __debug__: print("getFollows: ", follows, file=sys.stderr)
        db_follows_p = shelve.open(db_path + 'follows')
        db_follows_dict = db_follows_p.setdefault('FOLLOWS', OrderedDict())
        # merge 两个字典，为了保证顺序，目前仅发现下面这种方法有效
        mergeDict = db_follows_dict.copy()
        mergeDict.update(follows)
        db_follows_p["FOLLOWS"] = mergeDict
        db_follows_p.close()
    except IOError as err:
        print("save follows user id dict to shelve fail!", file=sys.stderr)
        print("IOError: ", err, file=sys.stderr)
        return False


import pytz
# from django.until import timezone
def covert2DjangoDateTime(_strPub_date):
    # pub_data format: '2018-10-31 10:13:25'
    # defualt datetime(1970, 1, 1, 0, 0, 0)
    _date, _time = _strPub_date.split(' ')
    _year, _month, _day = _date.split('-')
    _hour, _minte, _second = _time.split(':')
    return datetime(int(_year), int(_month), int(_day),
                    int(_hour), int(_minte), int(_second),
                    tzinfo=pytz.timezone('Asia/Shanghai'))


def startcrawler(request):
    # do the crawler action
    try:
        USER_ID = request.GET['user_id']
    except KeyError:
        print("WARNING: no 'user_id' in Request, crawler myself information!",
              file=sys.stderr)
        USER_ID = "qq_29757283"

    # -[o] joseph, 爬虫失败的情况这里没有考虑。
    try:
        userid = UserID.objects.get(user_id=USER_ID)  # 该用法没有问题。
    except UserID.DoesNotExist:
        userid = UserID.objects.create(user_id=USER_ID)  # TDDwithPython &5.6
        # save_all_follows_of_new_userid_to_shelve(
        #     USER_ID, "/mnt/sandi_TF/Plateform/database/follows_shelve/")
    if doDebug:
        print("userid: ", userid)

    newVisualData = VisualData()

    # myCSDNInfo = personalProfile.UserData(
    #     USER_ID, doDebug=False, browser_path='/opt/phantomjs/bin/phantomjs')
    myCSDNInfo = UserData(USER_ID, doDebug=False, )

    if True:  # multiprocessing version
        user_data_dict = myCSDNInfo.quikSyncCSDNData()
        print(user_data_dict, file=sys.stderr)

        if user_data_dict['originality'] in (0, -1):
            # CSDN 的 “三无” 用户
            # 准备一个节省资源的黑名单机制，名单中的用户 2 个月检查一次
            pass
        else:
            userid.visit = user_data_dict['beAccessed']
            userid.rank = user_data_dict['rank']
            userid.save()

            newVisualData.user_id = userid
            newVisualData.originality = user_data_dict['originality']
            newVisualData.fans = user_data_dict['fans']
            newVisualData.likes = user_data_dict['beLiked']
            newVisualData.comments = user_data_dict['beCommented']
            newVisualData.csdnLevel = user_data_dict['csdnLevel']
            newVisualData.visitors = user_data_dict['beAccessed']
            newVisualData.intergration = user_data_dict['membPoints']
            newVisualData.rank = user_data_dict['rank']
            newVisualData.save()

    if False:  # save the articles
        csdn_userid_articles = PersonalArticles(USER_ID)
        csdn_userid_articles.syncArticlesData()
        articlesInfo = csdn_userid_articles.articles
        # -[o] 重复的就不要保存了！
        while True:
            try:
                k, v = articlesInfo.popitem()
                newArticlesData = Article()
                newArticlesData.articleid = k
                newArticlesData.originality = v['originality']
                newArticlesData.title = v['title']
                newArticlesData.pub_date = covert2DjangoDateTime(v['pub_date'])
                newArticlesData.read_num = v['read_num']
                newArticlesData.comments_num = v['comment_num']
                newArticlesData.user_id = userid
                newArticlesData.save()
            except KeyError:  # pop until empty
                break

    if False:  # add follows part:
        one_of_follows = dict()
        try:
            dbp = shelve.open(
                "/mnt/sandi_TF/Plateform/database/follows_shelve/"+'follows')
            ordereddict_follows = dbp['FOLLOWS']
            webname, v = ordereddict_follows.popitem()
            one_of_follows[webname] = v
            dbp['FOLLOWS'] = ordereddict_follows  # 删除 pop 的 user
        except IOError:
            one_of_follows = None
        finally:
            # if 'dbp' in locals():
            dbp.close()
        if __debug__:
            print("new missions: \n", one_of_follows, "\n", file=sys.stderr)
        context = {'new_missions': one_of_follows}
    elif False:  # loop user id database part:
        one_user_id_in_db = ''
        try:
            dbp = shelve.open(
                "/mnt/sandi_TF/Plateform/database/follows_shelve/"+'UserID')
            all_user_ids = dbp['ALL_USER_IDs']
            one_user_id_in_db = all_user_ids.pop()
            dbp['ALL_USER_IDs'] = all_user_ids
        except IOError:
            one_user_id_in_db = None
        finally:
            # if 'dbp' in locals():
            dbp.close()
        if __debug__:
            print("new missions: \n", one_user_id_in_db, "\n", file=sys.stderr)
        context = {'new_missions': {"UserID": one_user_id_in_db}}
    else:
        context = {"new_missions": {"UserID": None}}
    return render(request, 'visualize/mission.html', context)


def loopArticles(request):
    try:
        USER_ID = request.GET['user_id']
    except KeyError:
        print("WARNING: no 'user_id' in 'loop Articles' Request, do nothing!",
              file=sys.stderr)
        return HttpResponse("<h1>WARNING: Should have User ID in URL</h1>")

    try:
        userid = UserID.objects.get(user_id=USER_ID)  # 该用法没有问题。
    except UserID.DoesNotExist:
        userid = UserID.objects.create(user_id=USER_ID)  # TDDwithPython &5.6
        # save_all_follows_of_new_userid_to_shelve(
        #     USER_ID, "/mnt/sandi_TF/Plateform/database/follows_shelve/")
    if doDebug:
        print("userid: ", userid)

    # -[x] 重复的就不要保存了！
    if len(userid.article_set.all()) != 0:
        return HttpResponse("<h1>Already Exists</h1>")

    # if False:  # save the articles
    try:
        csdn_userid_articles = PersonalArticles(USER_ID)
        csdn_userid_articles.syncArticlesData()
        articlesInfo = csdn_userid_articles.articles
        while True:
            try:
                k, v = articlesInfo.popitem()
                if k == "82762601":
                    # CSDN hide article - inside format - not be real
                    continue
                newArticlesData = Article()
                newArticlesData.articleid = k
                newArticlesData.originality = v['originality']
                newArticlesData.title = v['title']
                newArticlesData.pub_date = covert2DjangoDateTime(v['pub_date'])
                newArticlesData.read_num = v['read_num']
                newArticlesData.comments_num = v['comment_num']
                newArticlesData.user_id = userid
                newArticlesData.save()
            except KeyError:  # pop until empty
                break
    except CrawlerTimeoutError:
        return HttpResponse("<h1>Timeout</h1>")
    except CrawlerError:
        return HttpResponse("<h1>CrawlerError</h1>")
    else:
        return HttpResponse("<h1>OK</h1>")


def cleandata(request):
    try:
        dbp = shelve.open("/mnt/sandi_TF/Plateform/database/follows_shelve/"+'UserID')
        user_ids = UserID.objects.all()
        all_user_ids = list()
        all_user_ids = [userid.user_id for userid in user_ids]
        all_user_ids.reverse()  # 反转，从尾到头。这样 .pop() 的时候是从头开始。
        dbp['ALL_USER_IDs'] = all_user_ids
    finally:
        if 'dbp' in locals():
            dbp.close()
    return HttpResponse("<h1>OK</h1>")


#################################################
#     API and visual data(Visualize) part       #
#################################################
class Site(object):
    def __init__(self):
        self.name = "CSDN"

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


def index(request):
    all_userid_list = UserID.objects.all()
    # all_userid_list[-10::-1]
    _len = len(all_userid_list)
    if _len > 10:
    	all_userid_list = [userid for userid in all_userid_list[_len - 10:_len]][::-1]
    return render(request, 'visualize/index.html',
                  {'all_userid_list': all_userid_list,
                   'site': Site()})


def detail(request, user_id_id):
    userid = get_object_or_404(UserID, pk=user_id_id)

    return render(request, 'visualize/detail.html',
                  {'userid': userid, })


def userid_add(request):
    if request.method == 'POST':
        try:
            data = request.POST["new_crawl_target"]
            '''
            data = json.loads(data)
            '''
            result = re.findall("^id: (.*) & name: (.*)$", data)
            if not request:
                raise Http404("wrong format")
            else:
                CSDN_UserID = result[0][0]
                CSDN_UserName = result[0][1]
                try:
                    objects = UserID.objects.all()
                    if CSDN_UserID not in [obj.user_id for obj in objects]:
                        UserID.objects.create(
                            user_id=CSDN_UserID, name=CSDN_UserName)
                        return redirect("/" + "CSDNCrawler/")
                except Exception as err:
                    import traceback; traceback.print_exc();
                    raise Http404("server busy")

        except Exception as e:
            import traceback; traceback.print_exc();
            raise Http404("no new_crawl_target data")


def follows_detail_of_userid(request, pk):
    """ '/CSDNCrawler/userid/<pk>/follows/'
    """
    if request.method == 'GET':
        userid_obj = get_object_or_404(UserID, pk=pk)
        try:
            return render(request, "visualize/follows_detail.html",
                          {"userid_obj": userid_obj})
        except Exception:
            import traceback; traceback.print_exc();
            raise


class EasyDeltaDatetime():
    from datetime import datetime

    def __init__(self, dstDatetime, srcDatetime):
        self.dstDatetime = dstDatetime
        self.srcDatetime = srcDatetime
        self.computer_zero_datetime = datetime(1970, 1, 1, 0, 0, 0)
        self.calculate()

    def calculate(self):
        self.difference = self.dstDatetime - self.srcDatetime
        self.meta_datetime = self.computer_zero_datetime + self.difference

    def __getattr__(self, attrname):
        if attrname in ["year", "month", "day", "hour", "minute", "second"]:
            return int(getattr(self.meta_datetime, attrname) - getattr(self.computer_zero_datetime, attrname))


def crawl_follows(pk, pagesource=None):
    userid = get_object_or_404(UserID, pk=pk)
    f_all = userid.follows_set.all()
    if f_all:
        if EasyDeltaDatetime(
            datetime.now().replace(tzinfo=pytz.timezone("UTC")),
            f_all[len(f_all) - 1].crawledDate
        ).day < 3:
            return {"skip": "less than 3 days crawled"}
    try:
        socialData_by_userid = SocialData(
            userid.user_id,  # browser_path not be used for now.
            browser_path='/opt/phantomjs/bin/phantomjs',
            pagesource=pagesource)
        follows = socialData_by_userid.getFollows()
        # if __debug__:
        #     print("[Debug] id:{} getFollows: ".format(userid.user_id),
        #           follows, file=sys.stderr)
    except Exception:
        import traceback; traceback.print_exc();
        raise

    try:
        _f_d_in_DB = {_.follow_name: _.follow_id for _ in f_all}
        rsp_data = {}
        for k, v in follows.items():
            if _f_d_in_DB and (k, v) in _f_d_in_DB.items():
                continue  # skip
            f = userid.follows_set.create(
                follow_id=v, follow_name=k)
            # if __debug__:
            #     print("{!r}".format(f), file=sys.stderr)
            rsp_data[v] = [f.follow_name]
    except Exception:
        import traceback; traceback.print_exc();
        raise
    else:
        return rsp_data


def follows_crawl_of_userid(request, pk):
    """ '/CSDNCrawler/userid/<pk>/crawl/follows/'
    """
    if request.method == 'GET':
        try:
            rsp_data = crawl_follows(pk)
        except Exception:
            import traceback; traceback.print_exc();
            raise
        else:
            return JsonResponse(rsp_data)


def follows_get_of_userid(request, pk):
    userid = get_object_or_404(UserID, pk=pk)
    try:
        data = {idx: {"id": _.follow_id, "name": _.follow_name, "t_total": _.current_total_follows_num}
                for idx, _ in enumerate(userid.follows_set.all())}
        return JsonResponse(data)
    except Exception:
        import traceback; traceback.print_exc();
        raise
