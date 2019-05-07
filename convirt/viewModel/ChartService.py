#   ConVirt   -  Copyright (c) 2008 Convirture Corp.
#   ======
#
# ConVirt is a Virtualization management tool with a graphical user
# interface that allows for performing the standard set of VM operations
# (start, stop, pause, kill, shutdown, reboot, snapshot, etc...). It
# also attempts to simplify various aspects of VM lifecycle management.
#
#
# This software is subject to the GNU General Public License, Version 2 (GPLv2)
# and for details, please consult it at:
#
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# author : Jd <jd_jedi@users.sourceforge.net>
#
# ChartService.py
#
#   This module contains code to return chart information to the Web UI

import Basic
from convirt.core.utils.utils import to_unicode,to_str
import convirt.core.utils.constants
constants = convirt.core.utils.constants
import traceback
from convirt.model.Metrics import MetricsService, MetricVMRaw, MetricVMCurr, MetricServerRaw, MetricServerCurr, DataCenterRaw, DataCenterCurr
from convirt.model import DBSession
from convirt.model.TopCache import TopCache
from datetime import datetime,timedelta
import calendar
from tg import session
import tg

import logging
LOGGER = logging.getLogger("convirt.viewModel")
#    VM_RAW = 1
#    VM_CURR = 2
#    VM_ROLLUP = 3
#    SERVER_RAW = 4
#    SERVER_CURR = 5
#    SERVER_ROLLUP = 6
#    SERVERPOOL_RAW = 7
#    SERVERPOOL_CURR = 8
#    SERVERPOOL_ROLLUP = 9
#    DATACENTER_RAW = 10
#    DATACENTER_CURR = 11
#    DATACENTER_ROLLUP = 12
#
#    METRIC_CPU='CPU'
#    METRIC_MEM='Memory'
#    DTD='DTD'
#    MTD='MTD'
#    WTD='WTD'
#    CUSTOM='CUSTOM'
class ChartService:
    def __init__(self):
        self.service = MetricsService()
        self.manager = Basic.getGridManager()
        self.utcoffset=None

    def metrics(self,auth):
        node_id='53c7a8bb-fc80-947d-f6c5-ab8f33d1be15'#VM
        node_id='04e059c6-264d-b1af-77dd-f0a62ae00c34'#NODE
        day1=datetime.utcnow()
        day2=datetime.utcnow() +timedelta(hours=-8)
        print day1,"--------",day2
        result=self.service.getRawData(node_id,SERVER_RAW,day2,day1)
        #print len(result),"-------",result
        data_list=[]
        for ls in result:
            print ls[0],"--",ls[1],"--",ls[len(ls)-1]
            dt=ls[len(ls)-1]
            millis=calendar.timegm(dt.timetuple()) * 1000
            print millis
            data_list.append(dict(cpu=ls[0],mem=ls[1],millis=millis))
        return data_list

    def get_chart_data(self,auth,node_id,node_type,metric,period,offset,frm,to,\
                    chart_type=None,avg_fdate=None,avg_tdate=None):
        
        self.utcoffset=timedelta(milliseconds=long(offset))
        print (self.utcoffset),"***************",datetime.utcnow()
        
        per_type='ROLLUP'
        rollup_type=constants.HOURLY
        time_format="%H:%M"
        xlabel=ylabel=label=''
        minTick='day'
        date2=datetime.utcnow() 
        date1=datetime.utcnow() +timedelta(days=-1)

        if period==constants.CUSTOM:
            per_type='ROLLUP'
            date2=constants.defaultDate+timedelta(milliseconds=long(to))
            date1=constants.defaultDate+timedelta(milliseconds=long(frm))
            
            td=date2-date1            
            if td.days>3:
                rollup_type=constants.DAILY
                minTick=[1,'day']
                xlabel="Time(days)"
                time_format="%b/%d"
            elif self.timedelta_seconds(td) < (12*60*60): #12hours
                per_type='RAW'
                rollup_type=constants.HOURLY
                minTick=[30,'minute']
                xlabel="Time(minutes)"
                time_format="%H:%M"
            else:
                rollup_type=constants.HOURLY
                minTick=[2,'hour']
                xlabel="Time(hours)"
                time_format="%H:%M"
        else:
            per_type='ROLLUP'
            if period==constants.HRS24:
                rollup_type=constants.HOURLY
                minTick=[2,'hour']
                xlabel="Time(hours)"
                time_format="%H:%M"
                date1=date2 +timedelta(days=-1)
            elif period==constants.HRS12:
                per_type='RAW'
                rollup_type=constants.HOURLY
                minTick=[30,'minute']
                xlabel="Time(minutes)"
                time_format="%H:%M"
                date1=date2 +timedelta(seconds=-(12*60*60))
            elif period==constants.DAYS7:
                rollup_type=constants.DAILY
                minTick=[1,'day']
                xlabel="Time(days)"
                time_format="%b/%d"
                date1=date2 +timedelta(weeks=-1)
            elif period==constants.DAYS30:
                rollup_type=constants.DAILY
                minTick=[2,'day']
                xlabel="Time(days)"
                time_format="%b/%d"
                date1=date2 +timedelta(days=-31)
            elif period==constants.DTD:
                date2=constants.defaultDate+timedelta(milliseconds=long(to))                
                date2=date2+self.utcoffset                
                date1=datetime(date2.year,date2.month,date2.day)-self.utcoffset
                date2=date2-self.utcoffset                
                rollup_type=constants.HOURLY
                minTick=[2,'hour']
                xlabel="Time(hours)"
                time_format="%H:%M"                
            elif period==constants.WTD:
                rollup_type=constants.DAILY
                minTick=[1,'day']
                xlabel="Time(days)"
                time_format="%b/%d"
                weekdays=date2.date().weekday()
                date1=datetime(date2.year,date2.month,date2.day) +\
                                timedelta(days=-weekdays)-self.utcoffset
                diff=(date2-date1).days
                if diff<3:
                    minTick=[4,'hour']
                    time_format="%b/%d:%H"
                    xlabel="Time(hours)"
                if diff<1:
                    minTick=[1,'hour']
                    time_format="%b/%d:%H"
                    xlabel="Time(hours)"
            elif period==constants.MTD:
                rollup_type=constants.DAILY
                minTick=[1,'day']
                xlabel="Time(days)"
                time_format="%b/%d"                
                date1=datetime(date2.year,date2.month,date2.day) +\
                                timedelta(days=-(date2.day-1))-self.utcoffset
                diff=(date2-date1).days
                if diff>8:
                    minTick=[2,'day']
                    xlabel="Time(days)"

#        if chart_type==constants.TOP5SERVERS:
#            date2=datetime.utcnow()
#            date1=datetime.utcnow() +timedelta(seconds=-3601)
#            minTick=[5,'minute']
#            xlabel="Time(minutes)"
#            time_format="%H:%M"            
        

        hr1=to_str(date1.hour)
        hr2=to_str(date2.hour)
        minute1=to_str(date1.minute)
        minute2=to_str(date2.minute)
        if date1.hour<10:
            hr1="0"+hr1
        if date2.hour<10:
            hr2="0"+hr2
        dt_str=to_str(date1.year)+"/"+to_str(date1.month)+"/"+to_str(date1.day)+" "+hr1+":"+minute1+" - "+\
            to_str(date2.year)+"/"+to_str(date2.month)+"/"+to_str(date2.day)+" "+hr2+":"+minute2
        if metric==constants.METRIC_CPU:
            ylabel="cpu(%)"
	elif metric==constants.METRIC_VMCPU:
            ylabel="vm cpu(%)"
        elif metric==constants.METRIC_MEM:
            ylabel="memory(%)"
        label=dt_str
                
        series=[]
        ymax=1
        avg=0.0
        show_avg=False
        if chart_type==constants.TOP5SERVERS:
            metric_type=self.get_metric_type(node_type, per_type)
            (series,ymax)=self.topNServers(auth,node_id,node_type,metric,metric_type,\
                                rollup_type,per_type,date1,date2,period)
        elif chart_type==constants.COMPARISONCHART:
            (series,ymax)=self.comparison_chart(auth,node_id,node_type,metric,-1,\
                                rollup_type,per_type,date1,date2,period)
        else:
            metric_type=self.get_metric_type(node_type, per_type)
            (series,ymax,avg,show_avg)=self.chart_series_data(node_id,node_type, metric,metric_type,\
                                rollup_type,per_type,date1,date2,avg_fdate,avg_tdate,period)

        if len(series)==0:
            series.append(dict(data=[],label=""))

        min=calendar.timegm(date1.timetuple()) * 1000
        max=calendar.timegm(date2.timetuple()) * 1000          
        
        return dict(time_format=time_format,label=label,xlabel=xlabel,ylabel=ylabel,\
                    show_avg=show_avg,avg=avg,min=min,max=max,ymax=ymax,minTick=minTick,series=series) 

    def chart_series_data(self,node_id,node_type, metric,metric_type,rollup_type,per_type,\
                            date1,date2,avg_fdate=None,avg_tdate=None,period=None):
        series=[]
        node_ids=[]
        node_ids.append(node_id)
        avg=0.0
        avg=False
        if avg_fdate is not None and avg_tdate is not None:
            avg=True
        result=self.get_metrics_data(node_ids,metric,metric_type,rollup_type,per_type,date1,date2,period,avg)
        show_avg=False
        if avg_fdate is not None and avg_tdate is not None:
            avg_tdate=constants.defaultDate+timedelta(milliseconds=long(avg_tdate))
            avg_fdate=constants.defaultDate+timedelta(milliseconds=long(avg_fdate))
            show_avg=True
#        else:
#            avg_fdate=date1
#            avg_tdate=date2
#            show_avg=False
            
            if per_type == "ROLLUP":
                avg=self.service.getRollupAvg(node_id,metric,metric_type,rollup_type,avg_fdate,avg_tdate)
            else:
                avg=self.service.getRawAvg(node_id,node_type, metric,metric_type,avg_fdate,avg_tdate) 

        (data_list,ymax)=self.get_series_data(result)
        series.append(dict(data=data_list,label=""))
        return (series,ymax,avg,show_avg)

    def topNServers(self,auth,node_id,node_type,metric,metric_type,rollup_type,per_type,date1,date2,period):
        series=[]
        series.append(dict(data=[],label=""))
        ymx=2

        srvrs=[]
        
        if node_type==constants.DATA_CENTER:
            site=auth.get_entity(node_id)
            grps=site.children
            for grp in grps:
                srvrs.extend(grp.children)
        elif node_type==constants.SERVER_POOL:
            grp=auth.get_entity(node_id)
            if grp is None:
                return (series,ymx)
            srvrs=grp.children        

        srvr_ids=[]
        srvr_dict={}
        for srvr in srvrs:            
            srvr_ids.append(srvr.entity_id)
            srvr_dict[srvr.entity_id]=srvr.name
            
        #print self.service.getRollupTop(node_ids,metric,metric_type,rollup_type,date1,date2)       
        dt2=datetime.utcnow() 
        dt1=dt2 +timedelta(seconds=-3601)
        
        data_list=[]
        tc=TopCache()
        data_list = tc.get_top_entities(node_id,node_type,metric,"topNservers",auth,constants.SERVER_RAW,srvr_ids,dt1,dt2)
        if per_type=='ROLLUP':
            metric_type=constants.SERVER_ROLLUP
        else:
            metric_type=constants.SERVER_RAW

        for data in data_list:
            srvr_ids=[]
            srvr_ids.append(data[1])
            result=self.get_metrics_data(srvr_ids,metric,metric_type,rollup_type,per_type,date1,date2,period)
            
            (data_list,ymax)=self.get_series_data(result)
            if ymax>ymx:
                ymx=ymax

            series.append(dict(data=data_list,label=srvr_dict[data[1]]))

        return (series,ymx)

    def comparison_chart(self,auth,node_id,node_type,metric,metric_type,rollup_type,per_type,date1,date2,period):

        series=[]
        series.append(dict(data=[],label=""))
        ymx=2

        node_ids=node_id.split('*')
        node_types=node_type.split('*')
        i=-1
        for node_id in node_ids:
            i+=1
            ent=auth.get_entity(node_id)
            if ent is None:
                continue

            node_ids=[]
            node_ids.append(node_id)

            metric_type=self.get_metric_type(node_types[i], per_type)
            result=self.get_metrics_data(node_ids,metric,metric_type,rollup_type,per_type,date1,date2,period)
            (data_list,ymax)=self.get_series_data(result)
            if ymax>ymx:
                ymx=ymax

            series.append(dict(data=data_list,label=ent.name))
        
        return (series,ymx)

    def get_metrics_data(self,node_id,metric,metric_type,rollup_type,per_type,date1,date2,period,avg=False):

        result=[]
        if period==constants.CUSTOM or avg == True:
            result=self.get_metrics_specific_value(node_id,metric,metric_type,rollup_type,per_type,date1,date2)
        else:
            from convirt.model.MetricCache import MetricCache
            mc=MetricCache()
            result=mc.metric_cache(node_id[0],metric,metric_type,rollup_type,per_type,date1,date2,period)
        return result

    def get_metrics_specific_value(self,node_id,metric,metric_type,rollup_type,per_type,date1,date2):
        result=[]
        if per_type=='ROLLUP':
            result=self.service.getRollupMetricData(node_id,metric,metric_type,rollup_type,date1,date2)
        else:
            result=self.service.getRawMetricData(node_id,metric,metric_type,date1,date2)

        return result

    def get_series_data(self,listdata):
        ymax=0
        data_list=[]
        for ls in listdata:
            #print ls[0],"--",ls[1]
            dt=ls[1]
            millis=calendar.timegm(dt.timetuple()) * 1000
            if ls[0]>ymax:
                ymax=ls[0]
            data_list.append(dict(metric=ls[0],millis=millis))
        if (100-ymax)<=10:
            ymax=100
        else:
            ymax=ymax+2

        return (data_list,ymax)

    def get_metric_type(self,node_type,per_type):
        nod_type=""
        if node_type==constants.DATA_CENTER:
            nod_type='DATACENTER'
        elif node_type==constants.SERVER_POOL:
            nod_type='SERVERPOOL'
        elif node_type==constants.MANAGED_NODE:
            nod_type='SERVER'
        elif node_type==constants.DOMAIN:
            nod_type='VM'

        metric_type=eval("constants."+nod_type+"_"+per_type)
        return metric_type

    def timedelta_seconds(self,td):
        return (td.days*86400000 + td.seconds*1000 + td.microseconds/1000)/1000
    
