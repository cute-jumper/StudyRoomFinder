#!/usr/bin/python
# -*- coding=utf-8 -*-
import urllib, urllib2, HTMLParser, sqlite3

buildings = ['一教', '二教', '三教一、二段', '三教三段', '四教', '五教', '六教A段', '西阶', '旧水', '新水', '旧经报告厅', '文科楼', '技科楼', '建管报告厅', '明理楼', '理科楼', '六教B、C段', '东阶']
class RoominfoParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.intag = 0
        self.conn = None
        self.cursor = None
        self.hasdata = 0
        self.name = ''
        self.id = id
        self.info = []
        self.insert = 'replace into classroom values (?'
        for i in range(43):
            self.insert = self.insert + ', ?'
        self.insert = self.insert + ')'
        
    def connect(self, dbname):
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()
        sqlstring = ''
        for i in range(42):
            sqlstring += ', info'+str(i)
        sqlstring = '''create table if not exists classroom(
building, name primary key'''+sqlstring + ');'
        # print sqlstring
        self.cursor.execute(sqlstring)

    def set_id(self, id_):
        self.id = id_
    
    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            # for i in attrs:
            #     print i,
            # print
            self.intag = 1#表示进入了td环境
            if ('align', 'left') in attrs:
                # print self.name
                if len(self.name) > 0:#加入上一行
                    # print 'self.info:', self.info
                    self.cursor.execute(self.insert, ((unicode(buildings[self.id-1], 'utf-8'), self.name)+tuple(self.info)))
                    self.conn.commit()
                self.name = ''
                self.info = []
                self.intag = 2#表示是每一行的第一列，准备读取name
            self.hasdata = 0#数据段是否为空
        if tag == 'div' and self.intag == 1:
            self.intag = 3#表示进入了div环境，准备获取有无课的data
    def handle_endtag(self, tag):
        if tag == 'td' and self.intag >= 2:
            if self.hasdata == 0 and self.intag == 3:
                self.info.append(u'空')#没有课，且经过了div环境，将要离开
            self.intag = -1#表示离开td
        if tag == 'tr' and self.intag == -1:#加入最后一行
            # print self.name
            if len(self.name) > 0:
                self.cursor.execute(self.insert, ((unicode(buildings[self.id-1], 'utf-8'), self.name)+tuple(self.info)))
                self.conn.commit()
                self.intag = 0

    def handle_data(self, data):
        if self.intag == 2:
            # print 'info:', data
            self.name += data.decode('gbk')
        elif self.intag == 3:
            # print 'info:', data.decode('gbk')
            self.info.append(data.decode('gbk'))
            self.hasdata = 1


if __name__ == '__main__':
    dbname = "classroom.db"
    parser = RoominfoParser()
    parser.connect(dbname)
    for i in range(1, 19):
        parser.set_id(i)
        data = urllib2.urlopen("http://myhome.tsinghua.edu.cn/classroom/room1.asp?building_id="+str(i)).read()
        parser.feed(data)

    # Convert format to plain text
    import codecs
    f = codecs.open("classroom", 'w+', 'utf-8')
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    res = cursor.execute('''select * from classroom''')
    for line in res:
        for i in line:
            if i == u'有课' or i == u'借用':
                f.write('1')
            elif i == u'空':
                f.write('0')
            else:
                f.write(i+' ')
        print >> f
