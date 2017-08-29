#encoding=utf-8
'''
代理插件
'''
import json
import time

def init(dbc,logger):
    global plugin_dbc,plugin_logger
    plugin_dbc = dbc
    plugin_logger = logger
    logger.info('Inited')

def getinfo(a):
    ret = []
    for i in plugin_dbc.get_all('Users',{}).limit(100):
        ret.append({'url_token':i['url_token']})
    return json.dumps(ret)

def showexec(args):
    args['user']['_id'] = str(args['user']['_id'])
    return json.dumps(args)

def insertProxies(args):
    jarr = json.loads(args['posts']['proxies'])
    for i in jarr:
        plugin_dbc.insert_one('proxies', i)
    ret = {'data':jarr,
           'state':200,
           'args':args}
    return json.dumps(ret)

def updateProxies(args):
    jarr = json.loads(args['posts']['proxies'])
    for i in jarr:
        plugin_dbc.update('proxies', {'ip':i['ip'],'port':i['port']}, {'last_check':i['last_check'],'alive':i['alive']})
    ret = {'data':jarr,
           'state':200,
           'args':args}
    return json.dumps(ret)

def getuncheckedProxies(args):
    if not 't' in args['requests']:
        args['requests']['t'] = 600
    if not 'num' in args['requests']:
        args['requests']['num'] = 20
    dbr = []
    for d in plugin_dbc.get_all('proxies', {'alive':1,'last_check': {'$lt':time.time() - int(args['requests']['t'])}}).limit(int(args['requests']['num'])):
        d['_id'] = str(d['_id'])
        dbr.append(d)

    ret = {'data':dbr,
           'state':200,
           'args':args}

    return json.dumps(ret)

def getProxies(args):
    if not 'num' in args['requests']:
        args['requests']['num'] = 20
    dbr = []
    rt = []
    for d in plugin_dbc.get_all('proxies', {'alive':1,'selected':0}).limit(int(args['requests']['num'])):
        rt.append(d)

    if len(rt) < int(args['requests']['num']):
        plugin_dbc.update('proxies', {}, {'selected': 0})
        rt = plugin_dbc.get_all('proxies', {'alive':1,'selected':0}).limit(int(args['requests']['num']))
    for d in rt:
        plugin_dbc.update('proxies',{'_id':d['_id']},{'selected':1})
        d['_id'] = str(d['_id'])
        dbr.append(d)

    ret = {'data':dbr,
           'state':200,
           'args':args}

    return json.dumps(ret)

def build_page(args):
    if 'sub' in args['requests']:
        return ({'sub':'sss'}, args['requests']['sub'])
    else:
        args['total'] = plugin_dbc.get_all('proxies', {}).count()
        args['alive'] = plugin_dbc.get_all('proxies', {'alive':1}).count()
        args['proxies'] = []
        id = 0
        for proxy in plugin_dbc.get_all('proxies', {'alive':1}).limit(20):
            id +=1
            proxy['id'] = id
            args['proxies'].append(proxy)
        return (args, 'main')