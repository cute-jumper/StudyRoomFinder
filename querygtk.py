#!/usr/bin/python
#-*-coding: utf-8-*-

import gtk
import sys
import string
import sqlite3
from RoominfoParser import buildings

def parse_nums(nums):
    t = nums.split(',')
    s = []
    for i in t:
        s = s+i.split(' ')
    s = filter(lambda i:i !='',s)
    n = []
    for i in s:
        if i.find('-') != -1:
            r = i.split('-')
            for j in range(string.atoi(r[0]), string.atoi(r[1])+1):
                n.append(str(j))
    s = s+n
    s = filter(lambda i:i.find('-') == -1 and 0 < string.atoi(i) < 7,s)
    print 's:',s
    return {}.fromkeys(s).keys()

class Pyapp(gtk.Window):
    def __init__(self):
        super(Pyapp, self).__init__()
        self.set_title("自习室查询系统")
        self.set_default_size(280, 400)
        self.set_position(gtk.WIN_POS_CENTER)
        building = gtk.combo_box_new_text()
        building.connect("changed", self.on_changed_building)
        for i in buildings:
            building.append_text(i)
            
        vbox = gtk.VBox(False, 2)
        hbox = gtk.HBox(True, 2)
        label = gtk.Label('教学楼')
        hbox.pack_start(label, False, True, 0)
        label = gtk.Label('星期')
        hbox.pack_start(label, False, True, 0)
        vbox.pack_start(hbox, False, False, 0)
        hbox = gtk.HBox(True, 2)
        hbox.pack_start(building, False, True, 0)
        weekday = gtk.combo_box_new_text()
        weekday.connect("changed", self.on_changed_weekday)
        weekday.append_text(u'周一')
        weekday.append_text(u'周二')
        weekday.append_text(u'周三')
        weekday.append_text(u'周四')
        weekday.append_text(u'周五')
        weekday.append_text(u'周六')
        weekday.append_text(u'周日')
        hbox.pack_start(weekday, False, True, 0)
        vbox.pack_start(hbox, False, False, 0)
        self.entry = gtk.Entry()
        vbox.pack_start(self.entry, False, False, 0)
        button = gtk.Button(u'查询')
        button.connect('clicked', self.on_clicked)
        vbox.pack_start(button, False, False)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox.pack_start(sw, True, True, 0)
        store = self.create_model([])
        treeView = gtk.TreeView(store)
        treeView.set_rules_hint(True)
        sw.add(treeView)
        self.create_columns(treeView)
        self.treeView = treeView
        self.add(vbox)
        self.connect("destroy", gtk.main_quit)
        self.sqlstring = 'select building, name from classroom where ';
        self.day = 0
        self.conn = sqlite3.connect('classroom.db')
        self.cursor = self.conn.cursor()
        self.set_icon_from_file('querygtk.png')
        self.show_all()
    def on_changed_building(self, widget):
        self.building = 'building="'+str(widget.get_active_text()+'" ')
    def on_changed_weekday(self, widget):
        self.day = widget.get_active()
    def on_clicked(self, widget):
        text = self.entry.get_text()
        self.nums = parse_nums(text)
        tmp = ""
        for i in self.nums:
            tmp += 'and info'+str(self.day*6+string.atoi(i)-1)+'="空" '
        commit = self.sqlstring + self.building + tmp
        print 'commit:', commit
        self.cursor.execute(commit)
        
        res = self.cursor.fetchall()
        store = self.create_model(res)
        columns = self.treeView.get_columns()
        for i in columns:
            self.treeView.remove_column(i)
        self.treeView.set_model(store)
        self.create_columns(self.treeView)
    def create_model(self, res):
        if res == []:
            return None
        store = gtk.ListStore(str, str, int)
        for line in res:
            print line[0], line[1].split('/')
            store.append([line[0], line[1].split('/')[0], string.atoi(line[1].split('/')[1])])
        return store
    def create_columns(self, treeView):
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Building", rendererText, text=0)
        column.set_sort_column_id(0)
        treeView.append_column(column)
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Classroom", rendererText, text=1)
        column.set_sort_column_id(1)
        treeView.append_column(column)
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Capacity", rendererText, text=2)
        column.set_sort_column_id(2)
        treeView.append_column(column) 

Pyapp()
gtk.main()

