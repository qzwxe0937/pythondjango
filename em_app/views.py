from django.contrib import messages
from django.shortcuts import HttpResponse, redirect, render
from django.template.defaulttags import register
from django.utils.encoding import escape_uri_path

from .forms import emCheckRecordForm
from .models import emCheckItem, emCheckRecord, emFatpDetail, emLine, emStation, emSchedule

import pandas as pd
import ast
import json
from datetime import datetime, timedelta


# Create your views here.


def checkBaseLayoutCookies(function):
    def _function(request, *args, **kwargs):
        # check function
        # use cookie keep line list

        _checkList = ['navbarLineList', 'stationTable']

        for _item in _checkList:
            if _item not in request.COOKIES:
                _navbarLineList = json.dumps(
                    str([i.name for i in emLine.objects.all().order_by('name')]))
                _stationEnNameDict = json.dumps(
                    str({i.name: i.enName for i in emStation.objects.all()}))

                # (request.COOKIES is just a dictionnary)
                request.COOKIES['navbarLineList'] = _navbarLineList
                request.COOKIES['stationEnNameDict'] = _stationEnNameDict

                # Render the template with original request
                _resp = function(request, *args, **kwargs)

                # Actually set the cookie.
                _resp.set_cookie('navbarLineList', _navbarLineList)
                _resp.set_cookie('stationEnNameDict', _stationEnNameDict)
                return _resp

        return function(request, *args, **kwargs)
    return _function


@register.filter
def percentage(_value):
    return '{:.2%}'.format(_value)


@register.filter
def station2EnName(_dictStr, _station):
    return ast.literal_eval(json.loads(_dictStr)).get(_station)


@register.filter
def enName2Station(_dictStr, _station):
    return {v: k for k, v in ast.literal_eval(json.loads(_dictStr)).items()}.get(_station)


@register.filter
def cookie2List(_listStr):
    return ast.literal_eval(json.loads(_listStr))


@register.filter
def dictGetValue(_dict, _key):
    return _dict.get(_key, '')


def checkTATstate(item):
    # TAT = today - nextcheckday
    # TAT > 0 過期
    # 0 <= abs(TAT) <= cycletime*0.2 Y
    if item['checktat'] > 0 or pd.isna(item['checktat']):
        return 'R'
    else:
        if abs(item['checktat']) < item['checkID__cycleTime'] * 0.2:
            return 'Y'
    return 'G'


@checkBaseLayoutCookies
def Index(request):
    df = pd.DataFrame(list(emFatpDetail.objects.all().values(
        'line__name', 'line__lineOwner', 'station__name', 'checkID__size',
        'checkID__cycleTime', 'lastRecordID__checkDate')))

    # empty df will cause to error
    if not df.empty:
        df['nextchecktime'] = pd.to_datetime(
            df['lastRecordID__checkDate']) + pd.to_timedelta(df['checkID__cycleTime'], unit='d')
        df['checktat'] = (pd.Timestamp.today() - df['nextchecktime']).dt.days
        df['checkstate'] = df.apply(checkTATstate, axis=1)

        TotalSummary = pd.crosstab(index=df['checkID__size'],
                                  columns=df['checkstate'],
                                  dropna=False).reindex(columns=['G', 'Y', 'R'],
                                                        fill_value=0)

        lineSummary = pd.crosstab(index=df['line__name'],
                                  columns=df['checkstate'],
                                  margins=True,
                                  margins_name='total',
                                  dropna=False).reindex(columns=['G', 'Y', 'R', 'total'],
                                                        fill_value=0)

        _stationOrder = [
            i.name for i in emStation.objects.all().order_by('orderNum')]

        stationSummary = pd.crosstab(index=[df['line__name'], df['station__name']],
                                     columns=df['checkstate'],
                                     normalize='index',
                                     dropna=True).reindex(columns=['G', 'Y', 'R'],
                                                          fill_value=0).reindex(index=_stationOrder,
                                                                                level=1)

        #arrange data
        TotalSummary = TotalSummary.to_dict('index')
        lineSummary = lineSummary.to_dict('index')
        stationSummary = {i: stationSummary.xs(i).to_dict(
            'index') for i in stationSummary.index.levels[0]}
        lineOwnerList = df.groupby('line__name').first().to_dict()['line__lineOwner']
    else:
        lineSummary = {}
        stationSummary = {}
        lineOwnerList = {}

    # load schedule(schedule can be empty)
    set_today = datetime.today().date()
    lineSchedule = pd.DataFrame(list(emSchedule.objects.filter(
        day__range=(set_today, (set_today + timedelta(days=6)))).values('line', 'day', 'periods')))

    if not lineSchedule.empty:
        lineSchedule = lineSchedule.loc[lineSchedule['periods'].str.len() > 2].groupby(
            'line').agg({'day': 'min'})
        if not lineSchedule.empty:
            lineSchedule['lastDay'] = (lineSchedule['day'] - set_today).dt.days
            lineSchedule = lineSchedule.to_dict()['lastDay']
        else:
            lineSchedule = {}
    else:
        lineSchedule = {}

    context = {
        'lineSummary': lineSummary,
        'stationSummary': stationSummary,
        'lineSchedule': lineSchedule,
        'lineOwnerList': lineOwnerList,
        'TotalSummary': TotalSummary,
    }

    return render(request, 'EM_index.html', context=context)


@checkBaseLayoutCookies
def Detail(request, line):
    df = pd.DataFrame(list(emFatpDetail.objects.filter(line__name=line).values(
        'station__name', 'checkID__checkID', 'checkID__cycleTime', 'checkID__explain', 'lastRecordID__checkDate')))
    df['nextchecktime'] = pd.to_datetime(
        df['lastRecordID__checkDate']) + pd.to_timedelta(df['checkID__cycleTime'], unit='d')
    df['checktat'] = (pd.Timestamp.today() - df['nextchecktime']).dt.days
    df['checkstate'] = df.apply(checkTATstate, axis=1)

    df['nextchecktime'] = df['nextchecktime'].dt.date

    totalGYR = df['checkstate'].value_counts().reindex(
        index=['G', 'Y', 'R'], fill_value=0)

    stationGYR = pd.crosstab(index=df['station__name'],
                             columns=df['checkstate'],
                             dropna=False).reindex(columns=['G', 'Y', 'R'],
                                                   fill_value=0)

    # stationGYR = {i: stationGYR.xs(i).to_dict() for i in stationGYR.index}

    df.fillna(value={'lastRecordID__checkDate': 'None',
                     'nextchecktime': 'None',
                     'checktat': 9999},
              inplace=True)

    df['checktat'] = df['checktat'].astype(int)

    context = {
        'lineDetail': df.to_dict('index'),
        'doughnutData': {
            'labels': totalGYR.index.tolist(),
            'values': totalGYR.tolist(),
        },
        'barData': {
            'labels': stationGYR.index.tolist(),
            'valuesG': stationGYR['G'].values.tolist(),
            'valuesY': stationGYR['Y'].values.tolist(),
            'valuesR': stationGYR['R'].values.tolist(),
        },
        'currentPath': {
            'page': '統計',
            'line': line,
        }
    }

    return render(request, 'EM_detail.html', context=context)


@checkBaseLayoutCookies
def Form(request, line, station):
    _line = emLine.objects.get(name=line)
    _station = emStation.objects.get(enName=station)
    if request.method == 'POST':
        form = emCheckRecordForm(
            request.POST, request.FILES, line=_line, station=_station)

        if form.is_valid():
            # form ok process
            posts = form.save(commit=False)

            posts.ipAddr = request.META.get('REMOTE_ADDR', '0.0.0.0')
            posts.giUser = request.META.get('REMOTE_USER', 'not_gi_user')

            posts.checkLine = _line.name
            posts.checkStation = _station.name

            posts.checkDate = datetime.today().date()

            posts.checkItems = '\n'.join(
                map(str, form.cleaned_data['formCheckItems']))

            posts.checkFileName = request.FILES['checkFile'].name

            posts.save()

            # update lastRecordID to emFatpDetail
            list(map(lambda i: emFatpDetail.objects.filter(line=_line, checkID=i).update(
                lastRecordID=posts.id), form.cleaned_data['formCheckItems']))

            messages.add_message(request, messages.INFO, '紀錄成功!')
            return redirect(Detail, line=line)
        else:
            # form error process
            messages.add_message(request, messages.INFO, '紀錄失敗!')

    form = emCheckRecordForm(line=_line, station=_station)

    lastRecordDate = emFatpDetail.objects.filter(line__name=line,
                                                 station__enName=station).values('checkID__checkID',
                                                                                 'lastRecordID__checkDate')

    context = {
        'form': form,
        'lastRecordDate': {i['checkID__checkID']: i['lastRecordID__checkDate'] for i in lastRecordDate},
        'currentPath': {
            'page': '保養',
            'line': line,
            'station': enName2Station(request.COOKIES['stationEnNameDict'], station),
        }
    }

    return render(request, 'EM_form.html', context=context)


@checkBaseLayoutCookies
def Record(request, line, station):
    stationName = enName2Station(request.COOKIES['stationEnNameDict'], station)
    recordList = emCheckRecord.objects.filter(
        checkLine=line, checkStation=stationName)
    context = {
        'recordList': recordList,
        'currentPath': {
            'page': '紀錄',
            'line': line,
            'station': stationName,
        }
    }

    return render(request, 'EM_record.html', context=context)


def RecordFileDownload(request, record_id):
    obj = emCheckRecord.objects.get(id=record_id)
    response = HttpResponse(obj.checkFile.read())
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(
        escape_uri_path(obj.checkFileName))
    return response


@checkBaseLayoutCookies
def FormAll(request, line):
    context = {
        'stationList': emLine.objects.get(name=line).station.all(),
        'currentPath': {
            'page': '保養',
            'line': line,
            'station': 'ALL',
        }
    }
    return render(request, 'EM_form_all.html', context=context)


@checkBaseLayoutCookies
def RecordAll(request, line):
    context = {
        'stationList': emLine.objects.get(name=line).station.all(),
        'currentPath': {
            'page': '紀錄',
            'line': line,
            'station': 'ALL',
        }
    }
    return render(request, 'EM_record_all.html', context=context)


@checkBaseLayoutCookies
def Schedule(request, line):
    set_today = datetime.today()
    #set_today = datetime(2019, 5, 23)
    day2Index = {(set_today + timedelta(days=i)).date(): i for i in range(7)}
    schedule_data = {i: {'day': i, 'periods': []} for i in range(7)}

    db_result = emSchedule.objects.filter(
        line=line,
        day__range=(set_today, (set_today + timedelta(days=6)))
    )

    for i in db_result:
        schedule_data[day2Index[i.day]]['periods'] = json.loads(i.periods)

    schedule_mode = 'edit' if request.user.is_staff else 'read'

    context = {
        'line': line,
        'schedule_setting': {
            'mode': schedule_mode,
            'days': [i.strftime('%Y-%m-%d') for i in list(day2Index.keys())],
            'data': list(schedule_data.values())
        },
        'currentPath': {
            'page': '7日保養排程',
            'line': line,
        }
    }

    return render(request, 'EM_schedule.html', context=context)


def scheduleUpload(request):
    for i in json.loads(request.POST['data']):
        emSchedule.objects.update_or_create(line=request.POST['line'],
                                            day=i['day'],
                                            defaults={'periods': json.dumps(i['periods'])})

    return HttpResponse(json.dumps({'result': 'ok'}), content_type='application/json')


def UploadTestData(request):
    df = pd.read_excel('testData.xlsx')

    for index, _row in df.iterrows():
        print(index, _row)
        emStation.objects.get_or_create(
            name=_row.station,
            enName=_row.stationid,
            defaults={'orderNum': index}
        )

    for _station in emStation.objects.all():
        for index, _row in df[df['station'] == _station.name].iterrows():
            emCheckItem.objects.get_or_create(
                station=_station,
                checkID=_row.checkid,
                defaults={'explain': _row.checkitem,
                          'cycleTime': _row.checkcycletime}
            )

    lineList = ('AsSyf', 'Assyh', 'Assyi', 'Assyj', 'Assyk')

    for _line in lineList:
        obj, created = emLine.objects.get_or_create(name=_line)
        for _station in emStation.objects.all():
            obj.station.add(_station)
        obj.save()

    # for _line in emLine.objects.all():
    #    for _checkItem in emCheckItem.objects.all():
    #        _date = df[df['checkid'] ==
    #                   _checkItem.checkID].iloc[0]['lastchecktime']
    #        emFatpDetail.objects.filter(line=_line, checkID=_checkItem).update(
    #            lastRecordDate=_date)

    return render(request, 'test.html', {'posts': 'UploadTestData OK'})
