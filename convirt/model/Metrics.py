
#!/usr/bin/env python 
#
#   ConVirt   -  Copyright (c) 2009 Convirture Corp.
#   ======
#
# ConVirt is a Virtualization management tool with a graphical user
# interface that allows for performing the standard set of VM operations
# (start, stop, pause, kill, shutdown, reboot, snapshot, etc...). It
# also attempts to simplify various aspects of VM lifecycle management.
#
#
# This software is subject to the GNU General Public License, Version 2 (GPLv2)
# and for details, please consult it at
#
#    http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
#   
#   
# author : ConVirt Team
#    

import tg
import time
import datetime
import calendar
from math import sqrt
from sqlalchemy import func
from convirt.core.utils.utils import to_unicode,to_str,getHexID, p_task_timing_start,p_task_timing_end
from convirt.core.utils.constants import DOMAIN
from datetime import datetime,date, timedelta
from convirt.model.ManagedNode import ManagedNode
from convirt.model import DBSession,metadata, DeclarativeBase
from sqlalchemy.types import Integer, Unicode, String, DateTime
from sqlalchemy.orm import mapper, relation, sessionmaker, column_property
from sqlalchemy.schema import Index
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Float
from convirt.core.utils.constants import * # as is used in other files.
import convirt.core.utils.utils
import transaction
constants = convirt.core.utils.constants
from convirt.model.VM import VM
from convirt.model.LockManager import LockManager
import logging
LOGGER = logging.getLogger("convirt.model")
MTR_LOGGER = logging.getLogger("METRICS_TIMING")

"""
Class to hold metrics information
"""
PURGE_TYPE = 0
PURGE_DATE = 1

class Metrics(DeclarativeBase):
    __tablename__ = "metrics"
    id = Column(Unicode(50), primary_key=True)
    metric_type = Column(Integer)
    state = Column(Unicode(50))
    entity_id = Column(Unicode(50))
    icol1 = Column(Integer)
    icol2 = Column(Integer)
    icol3 = Column(Integer)
    icol4 = Column(Integer)
    icol5 = Column(Integer)
    icol6 = Column(Integer)
    icol7 = Column(Integer)
    icol8 = Column(Integer)
    icol9 = Column(Integer)
    icol10 = Column(Integer)
    icol11 = Column(Integer)
    icol12 = Column(Integer)
    icol13 = Column(Integer)
    fcol1 = Column(Float)
    fcol2 = Column(Float)
    fcol3 = Column(Float)
    fcol4 = Column(Float)
    fcol5 = Column(Float)
    fcol6 = Column(Float)
    fcol7 = Column(Float)
    fcol8 = Column(Float)
    fcol9 = Column(Float)
    fcol10 = Column(Float)
    fcol11 = Column(Float)
    fcol12 = Column(Float)
    fcol13 = Column(Float)
    fcol14 = Column(Float)
    fcol15 = Column(Float)
    fcol16 = Column(Float)
    fcol17 = Column(Float)
    fcol18 = Column(Float)
    fcol19 = Column(Float)
    fcol20 = Column(Float)
    fcol21 = Column(Float)
    fcol22 = Column(Float)
    fcol23 = Column(Float)
    fcol24 = Column(Float)
    fcol25 = Column(Float)
    cdate = Column (DateTime(timezone=True))


    def __init__(self):
        pass

Index("m_eid_rype_cdate", Metrics.entity_id, Metrics.metric_type, Metrics.cdate)
Index("m_rype_cdate", Metrics.metric_type, Metrics.cdate) # For top queries. Bug # 1121

class MetricsCurr(DeclarativeBase):
    __tablename__ = "metrics_curr"
    id = Column(Unicode(50), primary_key=True)
    metric_type = Column(Integer)
    state = Column(Unicode(50))
    entity_id = Column(Unicode(50))
    icol1 = Column(Integer)
    icol2 = Column(Integer)
    icol3 = Column(Integer)
    icol4 = Column(Integer)
    icol5 = Column(Integer)
    icol6 = Column(Integer)
    icol7 = Column(Integer)
    icol8 = Column(Integer)
    icol9 = Column(Integer)
    icol10 = Column(Integer)
    icol11 = Column(Integer)
    icol12 = Column(Integer)
    icol13 = Column(Integer)
    fcol1 = Column(Float)
    fcol2 = Column(Float)
    fcol3 = Column(Float)
    fcol4 = Column(Float)
    fcol5 = Column(Float)
    fcol6 = Column(Float)
    fcol7 = Column(Float)
    fcol8 = Column(Float)
    fcol9 = Column(Float)
    fcol10 = Column(Float)
    fcol11 = Column(Float)
    fcol12 = Column(Float)
    fcol13 = Column(Float)
    fcol14 = Column(Float)
    fcol15 = Column(Float)
    fcol16 = Column(Float)
    fcol17 = Column(Float)
    fcol18 = Column(Float)
    fcol19 = Column(Float)
    fcol20 = Column(Float)
    fcol21 = Column(Float)
    fcol22 = Column(Float)
    fcol23 = Column(Float)
    fcol24 = Column(Float)
    fcol25 = Column(Float)
    cdate = Column (DateTime(timezone=True))


    def __init__(self):
        pass

Index("m_ct_eid_rype_cdate", MetricsCurr.entity_id, MetricsCurr.metric_type, MetricsCurr.cdate)


class MetricsArch(DeclarativeBase):
    __tablename__ = "metrics_arch"
    id = Column(Unicode(50), primary_key=True)
    metric_type = Column(Integer)
    rollup_type = Column(Integer)
    state = Column(Unicode(50))
    entity_id = Column(Unicode(50))
    icol1 = Column(Integer)
    icol2 = Column(Integer)
    icol3 = Column(Integer)
    icol4 = Column(Integer)
    icol5 = Column(Integer)
    icol6 = Column(Integer)
    icol7 = Column(Integer)
    icol8 = Column(Integer)
    icol9 = Column(Integer)
    icol10 = Column(Integer)
    icol11 = Column(Integer)
    icol12 = Column(Integer)
    icol13 = Column(Integer)
    icol14 = Column(Integer)
    icol15 = Column(Integer)
    icol16 = Column(Integer)
    icol17 = Column(Integer)
    icol18 = Column(Integer)
    icol19 = Column(Integer)
    icol20 = Column(Integer)
    fcol1 = Column(Float)
    fcol2 = Column(Float)
    fcol3 = Column(Float)
    fcol4 = Column(Float)
    fcol5 = Column(Float)
    fcol6 = Column(Float)
    fcol7 = Column(Float)
    fcol8 = Column(Float)
    fcol9 = Column(Float)
    fcol10 = Column(Float)
    fcol11 = Column(Float)
    fcol12 = Column(Float)
    fcol13 = Column(Float)
    fcol14 = Column(Float)
    fcol15 = Column(Float)
    fcol16 = Column(Float)
    fcol17 = Column(Float)
    fcol18 = Column(Float)
    fcol19 = Column(Float)
    fcol20 = Column(Float)
    fcol21 = Column(Float)
    fcol22 = Column(Float)
    fcol23 = Column(Float)
    fcol24 = Column(Float)
    fcol25 = Column(Float)
    fcol26 = Column(Float)
    fcol27 = Column(Float)
    fcol28 = Column(Float)
    fcol29 = Column(Float)
    fcol30 = Column(Float)
    fcol31 = Column(Float)
    fcol32 = Column(Float)
    fcol33 = Column(Float)
    fcol34 = Column(Float)
    fcol35 = Column(Float)
    fcol36 = Column(Float)
    fcol37 = Column(Float)
    fcol38 = Column(Float)
    fcol39 = Column(Float)
    fcol40 = Column(Float)
    fcol41 = Column(Float)
    fcol42 = Column(Float)
    fcol43 = Column(Float)
    fcol44 = Column(Float)
    fcol45 = Column(Float)
    fcol46 = Column(Float)
    fcol47 = Column(Float)
    fcol48 = Column(Float)
    fcol49 = Column(Float)
    fcol50 = Column(Float)
    fcol51 = Column(Float)
    fcol52 = Column(Float)
    fcol53 = Column(Float)
    fcol54 = Column(Float)
    fcol55 = Column(Float)
    fcol56 = Column(Float)
    fcol57 = Column(Float)
    fcol58 = Column(Float)
    fcol59 = Column(Float)
    fcol60 = Column(Float)
    fcol61 = Column(Float)
    fcol62 = Column(Float)
    fcol63 = Column(Float)
    fcol64 = Column(Float)
    fcol65 = Column(Float)
    fcol66 = Column(Float)
    fcol67 = Column(Float)
    fcol68 = Column(Float)
    fcol69 = Column(Float)
    fcol70 = Column(Float)
    fcol71 = Column(Float)
    fcol72 = Column(Float)
    fcol73 = Column(Float)
    fcol74 = Column(Float)
    fcol75 = Column(Float)
    fcol76 = Column(Float)
    fcol77 = Column(Float)
    fcol78 = Column(Float)
    fcol79 = Column(Float)
    fcol80 = Column(Float)
    fcol81 = Column(Float)
    fcol82 = Column(Float)
    fcol83 = Column(Float)
    fcol84 = Column(Float)
    fcol85 = Column(Float)
    fcol86 = Column(Float)
    fcol87 = Column(Float)
    fcol88 = Column(Float)
    fcol89 = Column(Float)
    fcol90 = Column(Float)
    fcol91 = Column(Float)
    fcol92 = Column(Float)
    fcol93 = Column(Float)
    fcol94 = Column(Float)
    fcol95 = Column(Float)
    fcol96 = Column(Float)
    fcol97 = Column(Float)
    fcol98 = Column(Float)
    fcol99 = Column(Float)
    fcol100 = Column(Float)
    fcol101 = Column(Float)
    cdate = Column (DateTime(timezone=True))


    def __init__(self):
        pass

Index("m_ar_eid_rype_cdate", MetricsArch.entity_id, MetricsArch.metric_type, MetricsArch.rollup_type, MetricsArch.cdate)

class rollupStatus(DeclarativeBase):
    __tablename__ = "rollup_status"
    id = Column(Integer, primary_key=True)
    last_rollup_time = Column('last_rollup_time',DateTime(timezone=True))
    rollup_type = Column('rollup_type', Integer)
    entity_id = Column('entity_id',Unicode(50))

    def __init__(self):
        pass

Index("rlupstat_eid_rtype", rollupStatus.entity_id,rollupStatus.rollup_type)

class PurgeConfiguration(DeclarativeBase):
    __tablename__ = "purge_config"
    id = Column(Integer, primary_key=True)
    entity_id = Column('entity_id',Unicode(50))
    data_type = Column('data_type',Integer)
    retention_days = Column('retention_days',Integer)
 
    def __init__(self):
        pass

Index("prgeconfig_eid", PurgeConfiguration.entity_id)

class DataCenterRaw(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id=None
        self.state=None
        self.metric_type=constants.DATACENTER_RAW
        self.cdate=None
        self.cpu_util=None
        self.mem_util=None 
        self.vbds=None
        self.vbd_oo=None
        self.vbd_rd=None
        self.vbd_wr=None
        self.nets=None
        self.net_tx=None
        self.net_rx=None
        self.gb_local=None
        self.gb_poolused=None
        self.gb_pooltotal=None
    def __repr__(self):
        return "( DATA CENTER " + self.entity_id+ "," + to_str(self.state) + "," + to_str(self.metric_type) + "," + to_str(self.cdate)+","+to_str(self.cpu_util)+","+to_str(self.mem_util)+","+to_str(self.vbds)+","+to_str(self.vbd_oo)+","+to_str(self.vbd_rd)+","+to_str(self.vbd_wr)+","+to_str(self.nets)+","+to_str(self.net_tx)+","+to_str(self.net_rx)+","+to_str(self.gb_local)+","+to_str(self.gb_poolused)+","+to_str(self.gb_pooltotal) + ")"

class DataCenterRollup(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id=None 
        self.state=None
        self.metric_type=constants.DATACENTER_ROLLUP
        self.rollup_type=constants.HOURLY
        self.cdate=None
        self.cpu_util_avg=None
        self.cpu_util_min=None
        self.cpu_util_max=None
        self.cpu_util_stddev=None
        self.mem_util_avg=None
        self.mem_util_min=None
        self.mem_util_max=None
        self.mem_util_stddev=None
        self.vbds_avg=None
        self.vbds_min=None
        self.vbds_max=None
        self.vbds_stddev=None
        self.vbd_oo_avg=None
        self.vbd_oo_min=None
        self.vbd_oo_max=None
        self.vbd_oo_stddev=None
        self.vbd_rd_avg=None
        self.vbd_rd_min=None
        self.vbd_rd_max=None
        self.vbd_rd_stddev=None
        self.vbd_wr_avg=None
        self.vbd_wr_min=None
        self.vbd_wr_max=None
        self.vbd_wr_stddev=None
        self.nets_avg=None
        self.nets_min=None
        self.nets_max=None
        self.nets_stddev=None
        self.net_tx_avg=None
        self.net_tx_min=None
        self.net_tx_max=None
        self.net_tx_stddev=None
        self.net_rx_avg=None
        self.net_rx_min=None
        self.net_rx_max=None
        self.net_rx_stddev=None
        self.gb_local_avg=None
        self.gb_local_min=None
        self.gb_local_max=None
        self.gb_local_stddev=None
        self.gb_poolused_avg=None
        self.gb_poolused_min=None
        self.gb_poolused_max=None
        self.gb_poolused_stddev=None
        self.gb_pooltotal_avg=None
        self.gb_pooltotal_min=None
        self.gb_pooltotal_max=None
        self.gb_pooltotal_stddev=None
    
    def __repr__(self):
        return "( DATACENTER_ROLLUP " +to_str(self.type)+","+to_str(self.cpu_util_avg) +")"

class DataCenterCurr(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id=None
        self.state=None
        self.metric_type=constants.DATACENTER_CURR
        self.cdate=None
        self.cpu_util=None
        self.mem_util=None 
        self.vbds=None
        self.vbd_oo=None
        self.vbd_rd=None
        self.vbd_wr=None
        self.nets=None
        self.net_tx=None
        self.net_rx=None
        self.gb_local=None
        self.gb_poolused=None
        self.gb_pooltotal=None
    def __repr__(self):
        return "( DATACENTER_CURR "  +  self.entity_id+ "," + to_str(self.state) + "," + to_str(self.metric_type) + "," + to_str(self.cdate)+","+ to_str(self.cpu_util)+","+ to_str(self.mem_util)+","+ to_str(self.vbds)+","+ to_str(self.vbd_oo)+","+ to_str(self.vbd_rd)+","+ to_str(self.vbd_wr)+","+ to_str(self.nets)+","+ to_str(self.net_tx)+","+ to_str(self.net_rx)+","+ to_str(self.gb_local)+","+ to_str(self.gb_poolused)+","+ to_str(self.gb_pooltotal) +")"


class ServerPoolRaw(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id=None
        self.state=None
        self.metric_type=constants.SERVERPOOL_RAW
        self.cdate=None
        self.cpu_util=None
        self.mem_util=None 
        self.vbds=None
        self.vbd_oo=None
        self.vbd_rd=None
        self.vbd_wr=None
        self.nets=None
        self.net_tx=None
        self.net_rx=None
        self.gb_local=None
        self.gb_poolused=None
        self.gb_pooltotal=None
    def __repr__(self):
        return "( SERVERPOOL_RAW " +  self.entity_id+ "," + to_str(self.state) + "," + to_str(self.metric_type) + "," + to_str(self.cdate)+","+to_str(self.cpu_util)+","+to_str(self.mem_util)+","+to_str(self.vbds)+","+to_str(self.vbd_oo)+","+to_str(self.vbd_rd)+","+to_str(self.vbd_wr)+","+to_str(self.nets)+","+to_str(self.net_tx)+","+to_str(self.net_rx)+","+to_str(self.gb_local)+","+to_str(self.gb_poolused)+","+to_str(self.gb_pooltotal) + ")"


class ServerPoolRollup(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id=None 
        self.state=None
        self.metric_type=constants.SERVERPOOL_ROLLUP
        self.rollup_type=constants.HOURLY
        self.cdate=None
        self.cpu_util_avg=None
        self.cpu_util_min=None
        self.cpu_util_max=None
        self.cpu_util_stddev=None
        self.mem_util_avg=None
        self.mem_util_min=None
        self.mem_util_max=None
        self.mem_util_stddev=None
        self.vbds_avg=None
        self.vbds_min=None
        self.vbds_max=None
        self.vbds_stddev=None
        self.vbd_oo_avg=None
        self.vbd_oo_min=None
        self.vbd_oo_max=None
        self.vbd_oo_stddev=None
        self.vbd_rd_avg=None
        self.vbd_rd_min=None
        self.vbd_rd_max=None
        self.vbd_rd_stddev=None
        self.vbd_wr_avg=None
        self.vbd_wr_min=None
        self.vbd_wr_max=None
        self.vbd_wr_stddev=None
        self.nets_avg=None
        self.nets_min=None
        self.nets_max=None
        self.nets_stddev=None
        self.net_tx_avg=None
        self.net_tx_min=None
        self.net_tx_max=None
        self.net_tx_stddev=None
        self.net_rx_avg=None
        self.net_rx_min=None
        self.net_rx_max=None
        self.net_rx_stddev=None
        self.gb_local_avg=None
        self.gb_local_min=None
        self.gb_local_max=None
        self.gb_local_stddev=None
        self.gb_poolused_avg=None
        self.gb_poolused_min=None
        self.gb_poolused_max=None
        self.gb_poolused_stddev=None
        self.gb_pooltotal_avg=None
        self.gb_pooltotal_min=None
        self.gb_pooltotal_max=None
        self.gb_pooltotal_stddev=None
    def __repr__(self):
        return "( SERVERPOOL_ROLLUP" + to_str(self.type)+","+to_str(self.cpu_util_avg) +")"

class ServerPoolCurr(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id=None
        self.state=None
        self.metric_type=constants.SERVERPOOL_CURR
        self.cdate=None
        self.cpu_util=None
        self.mem_util=None 
        self.vbds=None
        self.vbd_oo=None
        self.vbd_rd=None
        self.vbd_wr=None
        self.nets=None
        self.net_tx=None
        self.net_rx=None
        self.gb_local=None
        self.gb_poolused=None
        self.gb_pooltotal=None
    def __repr__(self):
        return "( SERVERPOOL CURR " +  self.entity_id+ "," + to_str(self.state) + "," + to_str(self.metric_type) + "," + to_str(self.cdate)+","+to_str(self.cpu_util)+","+to_str(self.mem_util)+","+to_str(self.vbds)+","+to_str(self.vbd_oo)+","+to_str(self.vbd_rd)+","+to_str(self.vbd_wr)+","+to_str(self.nets)+","+to_str(self.net_tx)+","+to_str(self.net_rx)+","+to_str(self.gb_local)+","+to_str(self.gb_poolused)+","+to_str(self.gb_pooltotal) +")"


class MetricVMRaw(object): 
    def __init__(self):
        self.id = getHexID()
        self.entity_id=None
        self.state=None
        self.metric_type=constants.VM_RAW
        self.cdate=None
        self.cpu_util=None
        self.vm_cpu_util=None
        self.mem_util=None 
        self.vbds=None
        self.vbd_oo=None
        self.vbd_rd=None
        self.vbd_wr=None
        self.nets=None
        self.nets_tx=None
        self.nets_rx=None
        self.gb_local=None
        self.gb_poolused=None
        self.gb_pooltotal=None



    def __repr__(self):
        return "(" + to_str(self.cpu_util)+","+to_str(self.mem_util)+","+to_str(self.vbds)+","+to_str(self.vbd_oo)+","+to_str(self.vbd_rd)+","+to_str(self.vbd_wr)+","+to_str(self.nets)+","+to_str(self.nets_tx)+","+to_str(self.nets_rx)+","+to_str(self.gb_local)+","+to_str(self.gb_poolused)+","+to_str(self.gb_pooltotal) + ","+to_str(self.state) + ","+to_str(self.metric_type) +")"


class MetricServerRaw(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id=None
        self.state=None
        self.metric_type=constants.SERVER_RAW
        self.cdate=None
        self.cpu_util=None
        self.mem_util=None 
        self.vbds=None
        self.vbd_oo=None
        self.vbd_rd=None
        self.vbd_wr=None
        self.nets=None
        self.nets_tx=None
        self.nets_rx=None
        self.gb_local=None
        self.gb_poolused=None
        self.gb_pooltotal=None
        self.host_mem=None
        self.host_cpu=None
    def __repr__(self):
        return "( SERVER_RAW " + self.entity_id+ "," + to_str(self.state) + "," + to_str(self.metric_type) + "," + to_str(self.cdate)+","+to_str(self.cpu_util)+","+to_str(self.mem_util)+","+to_str(self.vbds)+","+to_str(self.vbd_oo)+","+to_str(self.vbd_rd)+","+to_str(self.vbd_wr)+","+to_str(self.nets)+","+to_str(self.nets_tx)+","+to_str(self.nets_rx)+","+to_str(self.gb_local)+","+to_str(self.gb_poolused)+","+to_str(self.gb_pooltotal) +")"


class MetricVMCurr(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id=None
        self.state=None
        self.metric_type=constants.VM_CURR
        self.cdate=None
        self.cpu_util=None
        self.vm_cpu_util=None
        self.mem_util=None 
        self.vbds=None
        self.vbd_oo=None
        self.vbd_rd=None
        self.vbd_wr=None
        self.nets=None
        self.nets_tx=None
        self.nets_rx=None
        self.gb_local=None
        self.gb_poolused=None
        self.gb_pooltotal=None
    def __repr__(self):
        return "( VM_CURR " + self.entity_id+ "," + to_str(self.state) + "," + to_str(self.metric_type) + "," + to_str(self.cdate)+","+to_str(self.cpu_util)+","+to_str(self.mem_util)+","+to_str(self.vbds)+","+to_str(self.vbd_oo)+","+to_str(self.vbd_rd)+","+to_str(self.vbd_wr)+","+to_str(self.nets)+","+to_str(self.net_tx)+","+to_str(self.net_rx)+","+to_str(self.gb_local)+","+to_str(self.gb_poolused)+","+to_str(self.gb_pooltotal) +")"


class MetricServerCurr(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id=None
        self.state=None
        self.metric_type=constants.SERVER_CURR
        self.cdate=None
        self.cpu_util=None
        self.mem_util=None 
        self.vbds=None
        self.vbd_oo=None
        self.vbd_rd=None
        self.vbd_wr=None
        self.nets=None
        self.nets_tx=None
        self.nets_rx=None
        self.gb_local=None
        self.gb_poolused=None
        self.gb_pooltotal=None
        self.host_mem=None
        self.host_cpu=None
    def __repr__(self):
        return "( SERVER_CURR " + self.entity_id+ "," + to_str(self.state) + "," + to_str(self.metric_type) + "," + to_str(self.cdate)+","+to_str(self.cpu_util)+","+to_str(self.mem_util)+","+to_str(self.vbds)+","+to_str(self.vbd_oo)+","+to_str(self.vbd_rd)+","+to_str(self.vbd_wr)+","+to_str(self.nets)+","+to_str(self.nets_tx)+","+to_str(self.nets_rx)+","+to_str(self.gb_local)+","+to_str(self.gb_poolused)+","+to_str(self.gb_pooltotal) +")"



class MetricVMRollup(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id=None 
        self.state=None
        self.metric_type=constants.VM_ROLLUP
        self.rollup_type=constants.HOURLY
        self.cdate=None
        self.cpu_util_avg=None
        self.cpu_util_min=None
        self.cpu_util_max=None
        self.cpu_util_stddev=None
        self.vm_cpu_util_avg=None
        self.vm_cpu_util_min=None
        self.vm_cpu_util_max=None
        self.vm_cpu_util_stddev=None
        self.mem_util_avg=None
        self.mem_util_min=None
        self.mem_util_max=None
        self.mem_util_stddev=None
        self.vbds_avg=None
        self.vbds_min=None
        self.vbds_max=None
        self.vbds_stddev=None
        self.vbd_oo_avg=None
        self.vbd_oo_min=None
        self.vbd_oo_max=None
        self.vbd_oo_stddev=None
        self.vbd_rd_avg=None
        self.vbd_rd_min=None
        self.vbd_rd_max=None
        self.vbd_rd_stddev=None
        self.vbd_wr_avg=None
        self.vbd_wr_min=None
        self.vbd_wr_max=None
        self.vbd_wr_stddev=None
        self.nets_avg=None
        self.nets_min=None
        self.nets_max=None
        self.nets_stddev=None
        self.net_tx_avg=None
        self.net_tx_min=None
        self.net_tx_max=None
        self.net_tx_stddev=None
        self.net_rx_avg=None
        self.net_rx_min=None
        self.net_rx_max=None
        self.net_rx_stddev=None
        self.gb_local_avg=None
        self.gb_local_min=None
        self.gb_local_max=None
        self.gb_local_stddev=None
        self.gb_poolused_avg=None
        self.gb_poolused_min=None
        self.gb_poolused_max=None
        self.gb_poolused_stddev=None
        self.gb_pooltotal_avg=None
        self.gb_pooltotal_min=None
        self.gb_pooltotal_max=None
        self.gb_pooltotal_stddev=None

    def __repr__(self):
        return "( VM_ROLLUP" + to_str(self.type)+","+to_str(self.cpu_util_avg) +")"


class MetricServerRollup(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id=None 
        self.state=None
        self.metric_type=constants.SERVER_ROLLUP
        self.rollup_type=constants.HOURLY
        self.cdate=None
        self.cpu_util_avg=None
        self.cpu_util_min=None
        self.cpu_util_max=None
        self.cpu_util_stddev=None
        self.mem_util_avg=None
        self.mem_util_min=None
        self.mem_util_max=None
        self.mem_util_stddev=None
        self.vbds_avg=None
        self.vbds_min=None
        self.vbds_max=None
        self.vbds_stddev=None
        self.vbd_oo_avg=None
        self.vbd_oo_min=None
        self.vbd_oo_max=None
        self.vbd_oo_stddev=None
        self.vbd_rd_avg=None
        self.vbd_rd_min=None
        self.vbd_rd_max=None
        self.vbd_rd_stddev=None
        self.vbd_wr_avg=None
        self.vbd_wr_min=None
        self.vbd_wr_max=None
        self.vbd_wr_stddev=None
        self.nets_avg=None
        self.nets_min=None
        self.nets_max=None
        self.nets_stddev=None
        self.net_tx_avg=None
        self.net_tx_min=None
        self.net_tx_max=None
        self.net_tx_stddev=None
        self.net_rx_avg=None
        self.net_rx_min=None
        self.net_rx_max=None
        self.net_rx_stddev=None
        self.gb_local_avg=None
        self.gb_local_min=None
        self.gb_local_max=None
        self.gb_local_stddev=None
        self.gb_poolused_avg=None
        self.gb_poolused_min=None
        self.gb_poolused_max=None
        self.gb_poolused_stddev=None
        self.gb_pooltotal_avg=None
        self.gb_pooltotal_min=None
        self.gb_pooltotal_max=None
        self.gb_pooltotal_stddev=None
        self.host_mem_avg=None
        self.host_mem_min=None
        self.host_mem_max=None
        self.host_mem_stddev=None
        self.host_cpu_avg=None
        self.host_cpu_min=None
        self.host_cpu_max=None
        self.host_cpu_stddev=None

    def __repr__(self):
        return "( SERVER_ROLLUP" + to_str(self.type)+","+to_str(self.cpu_util_avg) +")"


class MetricsService:

    def __init__(self):
        self.mapper_class_dict = self.mapper_class_lookup()
        self.metricType_class_dict = self.metricType_class_lookup()

    def mapper_class_lookup(self):
        mapper_class_dict  = {
                              'DataCenterRawMapper':DataCenterRaw,
                              'DataCenterCurrMapper':DataCenterCurr,
                              'DatCenterRollupMapper':DataCenterRollup,
                              'ServerPoolRawMapper':ServerPoolRaw,
                              'ServerPoolCurrMapper':ServerPoolCurr,
                              'ServerPoolRollupMapper':ServerPoolRollup,
                              'MetricVMRawMapper':MetricVMRaw,
                              'MetricServerRawMapper':MetricServerRaw,
                              'MetricVMCurrMapper':MetricVMCurr,
                              'MetricServerCurrMapper':MetricServerCurr,
                              'MetricVMRollupMapper':MetricVMRollup,
                              'MetricServerRollupMapper':MetricServerRollup
                             }
        return mapper_class_dict

    def metricType_class_lookup(self):
        metricType_class_dict = {
                                 constants.DATACENTER_RAW:DataCenterRaw,
                                 constants.DATACENTER_CURR:DataCenterCurr,
                                 constants.SERVERPOOL_RAW:ServerPoolRaw,
                                 constants.SERVERPOOL_CURR:ServerPoolCurr,
                                 constants.VM_RAW:MetricVMRaw,
                                 constants.SERVER_RAW:MetricServerRaw,
                                 constants.VM_CURR:MetricVMCurr,
                                 constants.SERVER_CURR:MetricServerCurr
                                 ,constants.DATACENTER_ROLLUP:DataCenterRollup,
                                 constants.SERVERPOOL_ROLLUP:ServerPoolRollup,
                                 constants.VM_ROLLUP:MetricVMRollup,
                                 constants.SERVER_ROLLUP:MetricServerRollup,
                                }
        return metricType_class_dict

    def init_mappers(self):
        # currently this mapper is not in use
        self.DataCenterRawMapper = mapper(DataCenterRaw,Metrics.__table__,properties={
        'entity_id':Metrics.__table__.c.entity_id,
        'state':Metrics.__table__.c.state,
        'metric_type':Metrics.__table__.c.metric_type,
        'cdate':Metrics.__table__.c.cdate,
        'cpu_util':Metrics.__table__.c.fcol1,
        'mem_util':Metrics.__table__.c.fcol2,
        'vbds':Metrics.__table__.c.icol1,
        'vbd_oo':Metrics.__table__.c.icol2,
        'vbd_rd':Metrics.__table__.c.icol3,
        'vbd_wr':Metrics.__table__.c.icol4,
        'nets':Metrics.__table__.c.icol5,
        'net_tx':Metrics.__table__.c.icol6,
        'net_rx':Metrics.__table__.c.icol7,
        'gb_local':Metrics.__table__.c.fcol3,
        'gb_poolused':Metrics.__table__.c.fcol4,
        'gb_pooltotal':Metrics.__table__.c.fcol5
        }
        )

        # currently this mapper is not in use
        self.DataCenterCurrMapper = mapper(DataCenterCurr,MetricsCurr.__table__,properties={
        'entity_id':column_property(MetricsCurr.__table__.c.entity_id),
        'state':column_property(MetricsCurr.__table__.c.state),
        'metric_type':column_property(MetricsCurr.__table__.c.metric_type),
        'cdate':column_property(MetricsCurr.__table__.c.cdate),
        'cpu_util':column_property(MetricsCurr.__table__.c.fcol1),
        'mem_util':column_property(MetricsCurr.__table__.c.fcol2),
        'vbds':column_property(MetricsCurr.__table__.c.icol1),
        'vbd_oo':column_property(MetricsCurr.__table__.c.icol2),
        'vbd_rd':column_property(MetricsCurr.__table__.c.icol3),
        'vbd_wr':column_property(MetricsCurr.__table__.c.icol4),
        'nets':column_property(MetricsCurr.__table__.c.icol5),
        'net_tx':column_property(MetricsCurr.__table__.c.icol6),
        'net_rx':column_property(MetricsCurr.__table__.c.icol7),
        'gb_local':column_property(MetricsCurr.__table__.c.fcol3),
        'gb_poolused':column_property(MetricsCurr.__table__.c.fcol4),
        'gb_pooltotal':column_property(MetricsCurr.__table__.c.fcol5)
        }
        )

        # currently this mapper is not in use 
        self.DatCenterRollupMapper = mapper(DataCenterRollup,MetricsArch.__table__,properties={
        'entity_id':MetricsArch.__table__.c.entity_id,
        'state':MetricsArch.__table__.c.state,
        'metric_type':MetricsArch.__table__.c.metric_type,
        'rollup_type':MetricsArch.__table__.c.rollup_type,
        'cdate':MetricsArch.__table__.c.cdate, 
        'cpu_util_avg':MetricsArch.__table__.c.fcol1,
        'cpu_util_min':MetricsArch.__table__.c.fcol2,
        'cpu_util_max':MetricsArch.__table__.c.fcol3,
        'cpu_util_stddev':MetricsArch.__table__.c.fcol4,
        'mem_util_avg':MetricsArch.__table__.c.fcol5,
        'mem_util_min':MetricsArch.__table__.c.fcol6,
        'mem_util_max':MetricsArch.__table__.c.fcol7,
        'mem_util_stddev':MetricsArch.__table__.c.fcol8,
        'vbds_avg':MetricsArch.__table__.c.fcol9,
        'vbds_min':MetricsArch.__table__.c.icol1,
        'vbds_max':MetricsArch.__table__.c.icol2,
        'vbds_stddev':MetricsArch.__table__.c.fcol9,
        'vbd_oo_avg':MetricsArch.__table__.c.icol3,
        'vbd_oo_min':MetricsArch.__table__.c.icol4,
        'vbd_oo_max':MetricsArch.__table__.c.icol5,
        'vbd_oo_stddev':MetricsArch.__table__.c.fcol10,
        'vbd_rd_avg':MetricsArch.__table__.c.fcol11,
        'vbd_rd_min':MetricsArch.__table__.c.icol6,
        'vbd_rd_max':MetricsArch.__table__.c.icol7,
        'vbd_rd_stddev':MetricsArch.__table__.c.icol8,
        'vbd_wr_avg':MetricsArch.__table__.c.fcol12,
        'vbd_wr_min':MetricsArch.__table__.c.icol9,
        'vbd_wr_max':MetricsArch.__table__.c.icol10,
        'vbd_wr_stddev':MetricsArch.__table__.c.fcol13,
        'nets_avg':MetricsArch.__table__.c.fcol14,
        'nets_min':MetricsArch.__table__.c.icol11,
        'nets_max':MetricsArch.__table__.c.icol12,
        'nets_stddev':MetricsArch.__table__.c.fcol15,
        'net_tx_avg':MetricsArch.__table__.c.fcol16,
        'net_tx_min':MetricsArch.__table__.c.icol13,
        'net_tx_max':MetricsArch.__table__.c.icol14,
        'net_tx_stddev':MetricsArch.__table__.c.fcol17,
        'net_rx_avg':MetricsArch.__table__.c.fcol18,
        'net_rx_min':MetricsArch.__table__.c.icol15,
        'net_rx_max':MetricsArch.__table__.c.icol16,
        'net_rx_stddev':MetricsArch.__table__.c.fcol19,
        'gb_local_avg':MetricsArch.__table__.c.fcol20,
        'gb_local_min':MetricsArch.__table__.c.fcol21,
        'gb_local_max':MetricsArch.__table__.c.fcol22,
        'gb_local_stddev':MetricsArch.__table__.c.fcol23,
        'gb_poolused_avg':MetricsArch.__table__.c.fcol24,
        'gb_poolused_min':MetricsArch.__table__.c.fcol25,
        'gb_poolused_max':MetricsArch.__table__.c.fcol26,
        'gb_poolused_stddev':MetricsArch.__table__.c.fcol27,
        'gb_pooltotal_avg':MetricsArch.__table__.c.fcol28,
        'gb_pooltotal_min':MetricsArch.__table__.c.fcol29,
        'gb_pooltotal_max':MetricsArch.__table__.c.fcol30,
        'gb_pooltotal_stddev':MetricsArch.__table__.c.fcol31,
        'cpu_util_stddev':MetricsArch.__table__.c.cdate
        }
        )

        self.ServerPoolRawMapper = mapper(ServerPoolRaw,Metrics.__table__,properties={
        'entity_id':column_property(Metrics.__table__.c.entity_id),
        'state':column_property(Metrics.__table__.c.state),
        'metric_type':column_property(Metrics.__table__.c.metric_type),
        'cdate':column_property(Metrics.__table__.c.cdate),
        'cpu_util':column_property(Metrics.__table__.c.fcol1),
        'mem_util':column_property(Metrics.__table__.c.fcol2),
        'vbds':column_property(Metrics.__table__.c.icol1),
        'vbd_oo':column_property(Metrics.__table__.c.icol2),
        'vbd_rd':column_property(Metrics.__table__.c.icol3),
        'vbd_wr':column_property(Metrics.__table__.c.icol4),
        'nets':column_property(Metrics.__table__.c.icol5),
        'net_tx':column_property(Metrics.__table__.c.icol6),
        'net_rx':column_property(Metrics.__table__.c.icol7),
        'gb_local':column_property(Metrics.__table__.c.fcol3),
        'gb_poolused':column_property(Metrics.__table__.c.fcol4),
        'gb_pooltotal':column_property(Metrics.__table__.c.fcol5),
        'total_vms':column_property(Metrics.__table__.c.icol8),
        'paused_vms':column_property(Metrics.__table__.c.icol9),
        'running_vms':column_property(Metrics.__table__.c.icol10),
        'server_cpus':column_property(Metrics.__table__.c.icol11),
        'crashed_vms':column_property(Metrics.__table__.c.icol12),
        'total_mem':column_property(Metrics.__table__.c.fcol6),
        'total_cpu':column_property(Metrics.__table__.c.fcol7),
        'server_mem':column_property(Metrics.__table__.c.fcol8),
        'server_count':column_property(Metrics.__table__.c.fcol9),
        'nodes_connected':column_property(Metrics.__table__.c.icol13)
        }
        )

        # currently this mapper is not in use
        self.ServerPoolCurrMapper = mapper(ServerPoolCurr,MetricsCurr.__table__,properties={
        'entity_id':column_property(MetricsCurr.__table__.c.entity_id),
        'state':column_property(MetricsCurr.__table__.c.state),
        'metric_type':column_property(MetricsCurr.__table__.c.metric_type),
        'cdate':column_property(MetricsCurr.__table__.c.cdate),
        'cpu_util':column_property(MetricsCurr.__table__.c.fcol1),
        'mem_util':column_property(MetricsCurr.__table__.c.fcol2),
        'vbds':column_property(MetricsCurr.__table__.c.icol1),
        'vbd_oo':column_property(MetricsCurr.__table__.c.icol2),
        'vbd_rd':column_property(MetricsCurr.__table__.c.icol3),
        'vbd_wr':column_property(MetricsCurr.__table__.c.icol4),
        'nets':column_property(MetricsCurr.__table__.c.icol5),
        'net_tx':column_property(MetricsCurr.__table__.c.icol6),
        'net_rx':column_property(MetricsCurr.__table__.c.icol7),
        'gb_local':column_property(MetricsCurr.__table__.c.fcol3),
        'gb_poolused':column_property(MetricsCurr.__table__.c.fcol4),
        'gb_pooltotal':column_property(MetricsCurr.__table__.c.fcol5),
        'total_vms':column_property(MetricsCurr.__table__.c.icol8),
        'paused_vms':column_property(MetricsCurr.__table__.c.icol9),
        'running_vms':column_property(MetricsCurr.__table__.c.icol10),
        'server_cpus':column_property(MetricsCurr.__table__.c.icol11),
        'crashed_vms':column_property(MetricsCurr.__table__.c.icol12),
        'total_mem':column_property(MetricsCurr.__table__.c.fcol6),
        'total_cpu':column_property(MetricsCurr.__table__.c.fcol7),
        'server_mem':column_property(MetricsCurr.__table__.c.fcol8),
        'server_count':column_property(MetricsCurr.__table__.c.fcol9),
        'nodes_connected':column_property(MetricsCurr.__table__.c.icol13)
        
        }
        )

        self.MetricServerRawMapper = mapper(MetricServerRaw,Metrics.__table__,properties={
        'entity_id':Metrics.__table__.c.entity_id,
        'state':Metrics.__table__.c.state,
        'metric_type':Metrics.__table__.c.metric_type,
        'cdate':Metrics.__table__.c.cdate,
        'cpu_util':Metrics.__table__.c.fcol1,
        'mem_util':Metrics.__table__.c.fcol2,
        'vbds':Metrics.__table__.c.icol1,
        'vbd_oo':Metrics.__table__.c.icol2,
        'vbd_rd':Metrics.__table__.c.icol3,
        'vbd_wr':Metrics.__table__.c.icol4,
        'nets':Metrics.__table__.c.icol5,
        'nets_tx':Metrics.__table__.c.icol6,
        'nets_rx':Metrics.__table__.c.icol7,
        'gb_local':Metrics.__table__.c.fcol3,
        'gb_poolused':Metrics.__table__.c.fcol4,
        'gb_pooltotal':Metrics.__table__.c.fcol5,
        'total_vms':Metrics.__table__.c.icol8,
        'paused_vms':Metrics.__table__.c.icol9,
        'running_vms':Metrics.__table__.c.icol10,
        'server_cpus':Metrics.__table__.c.icol11,
        'crashed_vms':Metrics.__table__.c.icol12,
        'total_mem':Metrics.__table__.c.fcol6,
        'total_cpu':Metrics.__table__.c.fcol7,
        'server_mem':Metrics.__table__.c.fcol8,
        'host_mem':Metrics.__table__.c.fcol9,
        'host_cpu':Metrics.__table__.c.fcol10
        }
        )

        # currently this mapper is not in use
        self.MetricServerCurrMapper = mapper(MetricServerCurr,MetricsCurr.__table__,properties={
        'entity_id':column_property(MetricsCurr.__table__.c.entity_id),
        'state':column_property(MetricsCurr.__table__.c.state),
        'metric_type':column_property(MetricsCurr.__table__.c.metric_type),
        'cdate':column_property(MetricsCurr.__table__.c.cdate),
        'cpu_util':column_property(MetricsCurr.__table__.c.fcol1),
        'mem_util':column_property(MetricsCurr.__table__.c.fcol2),
        'vbds':column_property(MetricsCurr.__table__.c.icol1),
        'vbd_oo':column_property(MetricsCurr.__table__.c.icol2),
        'vbd_rd':column_property(MetricsCurr.__table__.c.icol3),
        'vbd_wr':column_property(MetricsCurr.__table__.c.icol4),
        'nets':column_property(MetricsCurr.__table__.c.icol5),
        'nets_tx':column_property(MetricsCurr.__table__.c.icol6),
        'nets_rx':column_property(MetricsCurr.__table__.c.icol7),
        'gb_local':column_property(MetricsCurr.__table__.c.fcol3),
        'gb_poolused':column_property(MetricsCurr.__table__.c.fcol4),
        'gb_pooltotal':column_property(MetricsCurr.__table__.c.fcol5),
        'total_vms':column_property(MetricsCurr.__table__.c.icol8),
        'paused_vms':column_property(MetricsCurr.__table__.c.icol9),
        'running_vms':column_property(MetricsCurr.__table__.c.icol10),
        'server_cpus':column_property(MetricsCurr.__table__.c.icol11),
        'crashed_vms':column_property(MetricsCurr.__table__.c.icol12),
        'total_mem':column_property(MetricsCurr.__table__.c.fcol6),
        'total_cpu':column_property(MetricsCurr.__table__.c.fcol7),
        'server_mem':column_property(MetricsCurr.__table__.c.fcol8),
        'host_mem':column_property(MetricsCurr.__table__.c.fcol9),
        'host_cpu':column_property(MetricsCurr.__table__.c.fcol10)
        }
        )

        """
        serverrollup metrics is commented since the rollup data is added to server
        raw metrics. not sure if this mapper is required any more
        """
        self.MetricServerRollupMapper=mapper(MetricServerRollup,MetricsArch.__table__,properties={
        'entity_id':MetricsArch.__table__.c.entity_id,
        'state':MetricsArch.__table__.c.state,
        'metric_type':MetricsArch.__table__.c.metric_type,
        'rollup_type':MetricsArch.__table__.c.rollup_type,
        'cdate':MetricsArch.__table__.c.cdate, 
        'cpu_util_avg':MetricsArch.__table__.c.fcol1,
        'cpu_util_min':MetricsArch.__table__.c.fcol2,
        'cpu_util_max':MetricsArch.__table__.c.fcol3,
        'cpu_util_stddev':MetricsArch.__table__.c.fcol4,
        'mem_util_avg':MetricsArch.__table__.c.fcol5,
        'mem_util_min':MetricsArch.__table__.c.fcol6,
        'mem_util_max':MetricsArch.__table__.c.fcol7,
        'mem_util_stddev':MetricsArch.__table__.c.fcol8,
        'vbds_avg':MetricsArch.__table__.c.fcol9,
        'vbds_min':MetricsArch.__table__.c.icol1,
        'vbds_max':MetricsArch.__table__.c.icol2,
        'vbds_stddev':MetricsArch.__table__.c.fcol9,
        'vbd_oo_avg':MetricsArch.__table__.c.icol3,
        'vbd_oo_min':MetricsArch.__table__.c.icol4,
        'vbd_oo_max':MetricsArch.__table__.c.icol5,
        'vbd_oo_stddev':MetricsArch.__table__.c.fcol10,
        'vbd_rd_avg':MetricsArch.__table__.c.fcol11,
        'vbd_rd_min':MetricsArch.__table__.c.icol6,
        'vbd_rd_max':MetricsArch.__table__.c.icol7,
        'vbd_rd_stddev':MetricsArch.__table__.c.icol8,
        'vbd_wr_avg':MetricsArch.__table__.c.fcol12,
        'vbd_wr_min':MetricsArch.__table__.c.icol9,
        'vbd_wr_max':MetricsArch.__table__.c.icol10,
        'vbd_wr_stddev':MetricsArch.__table__.c.fcol13,
        'nets_avg':MetricsArch.__table__.c.fcol14,
        'nets_min':MetricsArch.__table__.c.icol11,
        'nets_max':MetricsArch.__table__.c.icol12,
        'nets_stddev':MetricsArch.__table__.c.fcol15,
        'nets_tx_avg':MetricsArch.__table__.c.fcol16,
        'nets_tx_min':MetricsArch.__table__.c.icol13,
        'nets_tx_max':MetricsArch.__table__.c.icol14,
        'nets_tx_stddev':MetricsArch.__table__.c.fcol17,
        'nets_rx_avg':MetricsArch.__table__.c.fcol18,
        'nets_rx_min':MetricsArch.__table__.c.icol15,
        'nets_rx_max':MetricsArch.__table__.c.icol16,
        'nets_rx_stddev':MetricsArch.__table__.c.fcol19,
        'gb_local_avg':MetricsArch.__table__.c.fcol20,
        'gb_local_min':MetricsArch.__table__.c.fcol21,
        'gb_local_max':MetricsArch.__table__.c.fcol22,
        'gb_local_stddev':MetricsArch.__table__.c.fcol23,
        'gb_poolused_avg':MetricsArch.__table__.c.fcol24,
        'gb_poolused_min':MetricsArch.__table__.c.fcol25,
        'gb_poolused_max':MetricsArch.__table__.c.fcol26,
        'gb_poolused_stddev':MetricsArch.__table__.c.fcol27,
        'gb_pooltotal_avg':MetricsArch.__table__.c.fcol28,
        'gb_pooltotal_min':MetricsArch.__table__.c.fcol29,
        'gb_pooltotal_max':MetricsArch.__table__.c.fcol30,
        'gb_pooltotal_stddev':MetricsArch.__table__.c.fcol31,
        #'cpu_util_stddev':MetricsArch.__table__.c.cdate,
        'host_mem_avg':MetricsArch.__table__.c.fcol32,
        'host_mem_min':MetricsArch.__table__.c.fcol33,
        'host_mem_max':MetricsArch.__table__.c.fcol34,
        'host_mem_stddev':MetricsArch.__table__.c.fcol35,
        'host_cpu_avg':MetricsArch.__table__.c.fcol36,
        'host_cpu_min':MetricsArch.__table__.c.fcol37,
        'host_cpu_max':MetricsArch.__table__.c.fcol38,
        'host_cpu_stddev':MetricsArch.__table__.c.fcol39
        }
        )

        self.ServerPoolRollupMapper=mapper(ServerPoolRollup,MetricsArch.__table__,properties={
        'entity_id':MetricsArch.__table__.c.entity_id,
        'state':MetricsArch.__table__.c.state,
        'metric_type':MetricsArch.__table__.c.metric_type,
        'rollup_type':MetricsArch.__table__.c.rollup_type,
        'cdate':MetricsArch.__table__.c.cdate, 
        'cpu_util_avg':MetricsArch.__table__.c.fcol1,
        'cpu_util_min':MetricsArch.__table__.c.fcol2,
        'cpu_util_max':MetricsArch.__table__.c.fcol3,
        'cpu_util_stddev':MetricsArch.__table__.c.fcol4,
        'mem_util_avg':MetricsArch.__table__.c.fcol5,
        'mem_util_min':MetricsArch.__table__.c.fcol6,
        'mem_util_max':MetricsArch.__table__.c.fcol7,
        'mem_util_stddev':MetricsArch.__table__.c.fcol8,
        'vbds_avg':MetricsArch.__table__.c.fcol9,
        'vbds_min':MetricsArch.__table__.c.icol1,
        'vbds_max':MetricsArch.__table__.c.icol2,
        'vbds_stddev':MetricsArch.__table__.c.fcol9,
        'vbd_oo_avg':MetricsArch.__table__.c.icol3,
        'vbd_oo_min':MetricsArch.__table__.c.icol4,
        'vbd_oo_max':MetricsArch.__table__.c.icol5,
        'vbd_oo_stddev':MetricsArch.__table__.c.fcol10,
        'vbd_rd_avg':MetricsArch.__table__.c.fcol11,
        'vbd_rd_min':MetricsArch.__table__.c.icol6,
        'vbd_rd_max':MetricsArch.__table__.c.icol7,
        'vbd_rd_stddev':MetricsArch.__table__.c.icol8,
        'vbd_wr_avg':MetricsArch.__table__.c.fcol12,
        'vbd_wr_min':MetricsArch.__table__.c.icol9,
        'vbd_wr_max':MetricsArch.__table__.c.icol10,
        'vbd_wr_stddev':MetricsArch.__table__.c.fcol13,
        'nets_avg':MetricsArch.__table__.c.fcol14,
        'nets_min':MetricsArch.__table__.c.icol11,
        'nets_max':MetricsArch.__table__.c.icol12,
        'nets_stddev':MetricsArch.__table__.c.fcol15,
        'nets_tx_avg':MetricsArch.__table__.c.fcol16,
        'nets_tx_min':MetricsArch.__table__.c.icol13,
        'nets_tx_max':MetricsArch.__table__.c.icol14,
        'nets_tx_stddev':MetricsArch.__table__.c.fcol17,
        'nets_rx_avg':MetricsArch.__table__.c.fcol18,
        'nets_rx_min':MetricsArch.__table__.c.icol15,
        'nets_rx_max':MetricsArch.__table__.c.icol16,
        'nets_rx_stddev':MetricsArch.__table__.c.fcol19,
        'gb_local_avg':MetricsArch.__table__.c.fcol20,
        'gb_local_min':MetricsArch.__table__.c.fcol21,
        'gb_local_max':MetricsArch.__table__.c.fcol22,
        'gb_local_stddev':MetricsArch.__table__.c.fcol23,
        'gb_poolused_avg':MetricsArch.__table__.c.fcol24,
        'gb_poolused_min':MetricsArch.__table__.c.fcol25,
        'gb_poolused_max':MetricsArch.__table__.c.fcol26,
        'gb_poolused_stddev':MetricsArch.__table__.c.fcol27,
        'gb_pooltotal_avg':MetricsArch.__table__.c.fcol28,
        'gb_pooltotal_min':MetricsArch.__table__.c.fcol29,
        'gb_pooltotal_max':MetricsArch.__table__.c.fcol30,
        'gb_pooltotal_stddev':MetricsArch.__table__.c.fcol31,
        'cpu_util_stddev':MetricsArch.__table__.c.cdate
        }
        )

        self.MetricVMRawMapper = mapper(MetricVMRaw,Metrics.__table__,properties={
        'entity_id':Metrics.__table__.c.entity_id,
        'state':Metrics.__table__.c.state,
        'metric_type':Metrics.__table__.c.metric_type,
        'cdate':Metrics.__table__.c.cdate,
        'cpu_util':Metrics.__table__.c.fcol1,
        'vm_cpu_util':Metrics.__table__.c.fcol6,
        'mem_util':Metrics.__table__.c.fcol2,
        'vbds':Metrics.__table__.c.icol1,
        'vbd_oo':Metrics.__table__.c.icol2,
        'vbd_rd':Metrics.__table__.c.icol3,
        'vbd_wr':Metrics.__table__.c.icol4,
        'nets':Metrics.__table__.c.icol5,
        'nets_tx':Metrics.__table__.c.icol6,
        'nets_rx':Metrics.__table__.c.icol7,
        'gb_local':Metrics.__table__.c.fcol3,
        'gb_poolused':Metrics.__table__.c.fcol4,
        'gb_pooltotal':Metrics.__table__.c.fcol5
        }
        )

        self.MetricVMCurrMapper = mapper(MetricVMCurr,MetricsCurr.__table__,properties={
        'entity_id':MetricsCurr.__table__.c.entity_id,
        'state':MetricsCurr.__table__.c.state,
        'metric_type':MetricsCurr.__table__.c.metric_type,
        'cdate':MetricsCurr.__table__.c.cdate,
        'cpu_util':MetricsCurr.__table__.c.fcol1,
        'vm_cpu_util':MetricsCurr.__table__.c.fcol6,
        'mem_util':MetricsCurr.__table__.c.fcol2,
        'vbds':MetricsCurr.__table__.c.icol1,
        'vbd_oo':MetricsCurr.__table__.c.icol2,
        'vbd_rd':MetricsCurr.__table__.c.icol3,
        'vbd_wr':MetricsCurr.__table__.c.icol4,
        'nets':MetricsCurr.__table__.c.icol5,
        'nets_tx':MetricsCurr.__table__.c.icol6,
        'nets_rx':MetricsCurr.__table__.c.icol7,
        'gb_local':MetricsCurr.__table__.c.fcol3,
        'gb_poolused':MetricsCurr.__table__.c.fcol4,
        'gb_pooltotal':MetricsCurr.__table__.c.fcol5
        }
        )

        self.MetricVMRollupMapper = mapper(MetricVMRollup,MetricsArch.__table__,properties={
        'entity_id':MetricsArch.__table__.c.entity_id,
        'state':MetricsArch.__table__.c.state,
        'metric_type':MetricsArch.__table__.c.metric_type,
        'rollup_type':MetricsArch.__table__.c.rollup_type,
        'cdate':MetricsArch.__table__.c.cdate, 
        'cpu_util_avg':MetricsArch.__table__.c.fcol1,
        'cpu_util_min':MetricsArch.__table__.c.fcol2,
        'cpu_util_max':MetricsArch.__table__.c.fcol3,
        'cpu_util_stddev':MetricsArch.__table__.c.fcol4,
        'vm_cpu_util_avg':MetricsArch.__table__.c.fcol40,
        'vm_cpu_util_min':MetricsArch.__table__.c.fcol41,
        'vm_cpu_util_max':MetricsArch.__table__.c.fcol42,
        'vm_cpu_util_stddev':MetricsArch.__table__.c.fcol43,
        'mem_util_avg':MetricsArch.__table__.c.fcol5,
        'mem_util_min':MetricsArch.__table__.c.fcol6,
        'mem_util_max':MetricsArch.__table__.c.fcol7,
        'mem_util_stddev':MetricsArch.__table__.c.fcol8,
        'vbds_avg':MetricsArch.__table__.c.fcol9,
        'vbds_min':MetricsArch.__table__.c.icol1,
        'vbds_max':MetricsArch.__table__.c.icol2,
        'vbds_stddev':MetricsArch.__table__.c.fcol9,
        'vbd_oo_avg':MetricsArch.__table__.c.icol3,
        'vbd_oo_min':MetricsArch.__table__.c.icol4,
        'vbd_oo_max':MetricsArch.__table__.c.icol5,
        'vbd_oo_stddev':MetricsArch.__table__.c.fcol10,
        'vbd_rd_avg':MetricsArch.__table__.c.fcol11,
        'vbd_rd_min':MetricsArch.__table__.c.icol6,
        'vbd_rd_max':MetricsArch.__table__.c.icol7,
        'vbd_rd_stddev':MetricsArch.__table__.c.icol8,
        'vbd_wr_avg':MetricsArch.__table__.c.fcol12,
        'vbd_wr_min':MetricsArch.__table__.c.icol9,
        'vbd_wr_max':MetricsArch.__table__.c.icol10,
        'vbd_wr_stddev':MetricsArch.__table__.c.fcol13,
        'nets_avg':MetricsArch.__table__.c.fcol14,
        'nets_min':MetricsArch.__table__.c.icol11,
        'nets_max':MetricsArch.__table__.c.icol12,
        'nets_stddev':MetricsArch.__table__.c.fcol15,
        'nets_tx_avg':MetricsArch.__table__.c.fcol16,
        'nets_tx_min':MetricsArch.__table__.c.icol13,
        'nets_tx_max':MetricsArch.__table__.c.icol14,
        'nets_tx_stddev':MetricsArch.__table__.c.fcol17,
        'nets_rx_avg':MetricsArch.__table__.c.fcol18,
        'nets_rx_min':MetricsArch.__table__.c.icol15,
        'nets_rx_max':MetricsArch.__table__.c.icol16,
        'nets_rx_stddev':MetricsArch.__table__.c.fcol19,
        'gb_local_avg':MetricsArch.__table__.c.fcol20,
        'gb_local_min':MetricsArch.__table__.c.fcol21,
        'gb_local_max':MetricsArch.__table__.c.fcol22,
        'gb_local_stddev':MetricsArch.__table__.c.fcol23,
        'gb_poolused_avg':MetricsArch.__table__.c.fcol24,
        'gb_poolused_min':MetricsArch.__table__.c.fcol25,
        'gb_poolused_max':MetricsArch.__table__.c.fcol26,
        'gb_poolused_stddev':MetricsArch.__table__.c.fcol27,
        'gb_pooltotal_avg':MetricsArch.__table__.c.fcol28,
        'gb_pooltotal_min':MetricsArch.__table__.c.fcol29,
        'gb_pooltotal_max':MetricsArch.__table__.c.fcol30,
        'gb_pooltotal_stddev':MetricsArch.__table__.c.fcol31,
        'cpu_util_stddev':MetricsArch.__table__.c.cdate
        }
        )

    def getClass(self, mapper_name):
        class_name = self.mapper_class_dict[mapper_name]
        return class_name

    def getClassfromMetricType(self, metric_type):
        class_name = self.metricType_class_dict[metric_type]
        return class_name

    def setClass(self, mapper_name, class_name):
        self.mapper_class_dict.update({mapper_name:class_name})

    def UpdateclassMetricTypeLookup(self, mapper_name, class_name):
        self.metricType_class_dict.update({mapper_name:class_name})



    #=========
    # ROLLUPS :
    #=========

    """
    function to insert record into rollup_status table if there is no entry in the table 
    """
    def insert_rollupstatus_record(self,entity_id,rollup_type):
        # Initialise default data
        defaultDate = constants.defaultDate
        try:
            # query rollupstatus table to read the last_rollup_time
            rollupStatusResult = DBSession.query(rollupStatus).filter(rollupStatus.entity_id==entity_id).filter(rollupStatus.rollup_type==rollup_type).first()
        except:
            rollupStatusResult = None

        # if table has record
        if  rollupStatusResult:
            # read the last_rollup_time
            defaultDate = rollupStatusResult.last_rollup_time
        else:
            # add new entry for given entity id with default date
            rollup_staus_obj = rollupStatus()
            rollup_staus_obj.last_rollup_time = defaultDate
            rollup_staus_obj.rollup_type = rollup_type
            rollup_staus_obj.entity_id = entity_id
            DBSession.add(rollup_staus_obj) 
        
        return defaultDate

    # function to update time stamp in rollup_status table if rollup is done
    def update_rollupstatus_record(self,entity_id,formatted_uptoDate,rollup_type):
        # query rollupstatus table to read the last_rollup_time
        try:
            rollupStatusResult = DBSession.query(rollupStatus).filter(rollupStatus.entity_id==entity_id).filter(rollupStatus.rollup_type==rollup_type).first()

            if rollupStatusResult:
                # update last_rollup_time
                rollupStatusResult.last_rollup_time = formatted_uptoDate
        except Exception, ex:
            LOGGER.error(to_str(ex))
            LOGGER.debug('Failed: update_rollupstatus_record')
            raise

    # function to find the date on weekend for previous week
    def find_date_for_week_rollup(self):
        """
        example for date 2009-10-10
        weekNo = 40
        first_date_of_year = 2009-01-01
        no_of_days = 273
        weekBeforeToDate = 2009-10-04
        """
        weekNo = int((datetime.utcnow().strftime("%U")))
        # first date of the current year
        first_date_of_year = date(datetime.utcnow().year,1,1)
        # find the day of the week as an integer sun = 7/mon = 1
        if(first_date_of_year.weekday()>3):
            # find the date of weekend i.e ( date on sunday of that week). needs to add number of days if weeday > 3
            last_date_week = first_date_of_year+timedelta(7-first_date_of_year.weekday())
        else:
            # find the date of weekend i.e ( date on sunday of last week). needs to sub if weekday < 3
            last_date_week = first_date_of_year - timedelta(first_date_of_year.weekday())
        # find number of days upto lastweek for current year
        no_of_days = timedelta(days = (weekNo-1)*7)
        # for date = (2009-10-10) weekBeforeToDate will be (2009-10-04)
        weekBeforeToDate = (last_date_week + no_of_days + timedelta(days=6))
        return weekBeforeToDate

    """
    function to find the last date of the month & year passed
    """
    def last_date_of_previous_month(self, year, month):
        """ Work out the last day of the month """
        last_days = [31, 30, 29, 28, 27]
        for i in last_days:
                try:
                        end = datetime(year, month, i)
                except ValueError:
                        continue
                else:
                        return end.date()
        return None

    # function to retrieve previous hour
    def get_previous_hour(self):
        todays_date = datetime.utcnow()
        hr = todays_date.strftime("%H")
        # check if it morning 00 hours
        if int(hr)==0:
            # change the day to previous day
            difference = timedelta(days=-1)
            uptoDate = (todays_date + difference).strftime("%Y-%m-%d %H")
        else:
            # to find the last hour
            uptoDate = datetime(todays_date.year,todays_date.month,todays_date.day,todays_date.hour-1, 59,59).strftime("%Y-%m-%d %H")
        return uptoDate

    # Insert data into metrics_arch 
    def insert_timebased_rollup_record(self, row, uptoDate, metricTypeRollup, rollup_type, entity_id):
        row=list(row)        
        for values in row:
            if values==None:
                row.__setitem__(row.index(values), 0)        
        
        id = getHexID()
        dburl = tg.config.get('sqlalchemy.url')
        db_type=dburl.split("/")        
        # query for inserting data into metrics_arch for rolledup data
        try:
            LockManager().get_lock(constants.METRICS,entity_id, constants.ROLLUP_METRICS, constants.Table_metrics_arch)

            if db_type[0]=="oracle:":
                try:
                    orac="insert into metrics_arch (id, fcol1, fcol2, fcol3, fcol5, fcol6, fcol7, fcol9,icol1, icol2, icol3, icol4, icol5, fcol11, icol6, icol7, fcol12, icol9, icol10, fcol14, icol11, icol12, fcol16, icol13, icol14, fcol18, icol15, icol16, fcol20, fcol21, fcol22, fcol24, fcol25, fcol26, fcol28, fcol29, fcol30, fcol32, fcol33, fcol34, fcol36, fcol37, fcol38, fcol40, fcol41, fcol42, cdate, metric_type, rollup_type, entity_id) values ('%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s', '%s')" % (id, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36], row[37], row[38], row[39], row[40], row[41], row[44], row[45], row[46], "to_date('" + to_str(uptoDate) + "','" + to_str("yyyy-mm-dd hh24:mi:ss") + "')", metricTypeRollup, rollup_type, entity_id)
                    LOGGER.debug(orac)
                    DBSession.execute(orac)
                except Exception, e:
                    import traceback
                    traceback.print_exc()
                    raise e
            else:
                DBSession.execute("insert into metrics_arch (id, fcol1, fcol2, fcol3, fcol5, fcol6, fcol7, fcol9,icol1, icol2, icol3, icol4, icol5, fcol11, icol6, icol7, fcol12, icol9, icol10, fcol14, icol11, icol12, fcol16, icol13, icol14, fcol18, icol15, icol16, fcol20, fcol21, fcol22, fcol24, fcol25, fcol26, fcol28, fcol29, fcol30, fcol32, fcol33, fcol34, fcol36, fcol37, fcol38, fcol40, fcol41, fcol42, cdate, metric_type, rollup_type, entity_id) values ('%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s', '%s', '%s')" % (id, row[0],row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36], row[37], row[38], row[39], row[40], row[41], row[44], row[45], row[46], uptoDate, metricTypeRollup, rollup_type, entity_id))
        finally:
            LockManager().release_lock()

    # Fetch rolled-up data for given entity_id and for given time criteria
    def fetch_timebased_rollup_records(self,date_format_string, groupby_format_string, defaultDate, uptoDate, entity_id, metricType, condition=""):
         # query to fetch rolled-up data for given entity_id for given time criteria 
        dburl = tg.config.get('sqlalchemy.url')
        db_type=dburl.split("/")

        if db_type[0]=="sqlite:":
           if groupby_format_string=='%U' :
               groupby_format_string='%W'
           resultSet = DBSession.execute('select avg(fcol1), min(fcol1), max(fcol1),avg(fcol2), min(fcol2), max(fcol2),avg(icol1), min(icol1), max(icol1),avg(icol2), min(icol2), max(icol2),avg(icol3), min(icol3), max(icol3),avg(icol4), min(icol4), max(icol4),avg(icol5), min(icol5), max(icol5),avg(icol6), min(icol6), max(icol6),avg(icol7), min(icol7), max(icol7),avg(fcol3), min(fcol3), max(fcol3),avg(fcol4), min(fcol4), max(fcol4),avg(fcol5), min(fcol5), max(fcol5),avg(fcol9),min(fcol9),max(fcol9),avg(fcol10),min(fcol10),max(fcol10),strftime("' + to_str(groupby_format_string) + '", ' +  'cdate'  + '),strftime("' + to_str(date_format_string) + '", ' +  'cdate'  + '), avg(fcol6), min(fcol6), max(fcol6)  from metrics where cdate>= "' + to_str(defaultDate) +'" and  cdate< "' + to_str(uptoDate) +'" and entity_id = "' + to_str(entity_id) + '" and metric_type = ' + to_str(metricType) + condition +' group by strftime("' + to_str(groupby_format_string) + '", ' +  'cdate'  + ');')

        elif db_type[0]=="mysql:":
           resultSet = DBSession.execute('select avg(fcol1), min(fcol1), max(fcol1),avg(fcol2), min(fcol2), max(fcol2),avg(icol1), min(icol1), max(icol1),avg(icol2), min(icol2), max(icol2),avg(icol3), min(icol3), max(icol3),avg(icol4), min(icol4), max(icol4),avg(icol5), min(icol5), max(icol5),avg(icol6), min(icol6), max(icol6),avg(icol7), min(icol7), max(icol7),avg(fcol3), min(fcol3), max(fcol3),avg(fcol4), min(fcol4), max(fcol4),avg(fcol5), min(fcol5), max(fcol5),avg(fcol9),min(fcol9),max(fcol9),avg(fcol10),min(fcol10),max(fcol10),date_format(cdate,"'+ to_str(groupby_format_string)+'"),date_format(cdate,"'+ to_str(date_format_string)+'"), avg(fcol6), min(fcol6), max(fcol6)  from metrics where cdate>= "' + to_str(defaultDate) +'" and  cdate< "' + to_str(uptoDate) +'" and entity_id = "' + to_str(entity_id) + '" and metric_type = ' + to_str(metricType) + condition +' group by date_format(cdate,"'+ to_str(groupby_format_string)+'" );')

        return resultSet

    def get_row_date(self, row, rollup_type):
        
        tmprow=list(row)        
        dateval=tmprow[43]
        year = int(dateval[:4])
        month =  int(dateval[5:7])

        if rollup_type==constants.HOURLY:
            day = int(dateval[8:10])
            hour = int(dateval[11:13])            
            rowdate = datetime(year, month, day, hour)
        elif rollup_type==constants.DAILY:
            day = int(dateval[8:10])            
            rowdate = datetime(year, month, day)
        elif rollup_type==constants.WEEKLY:
            day = int(dateval[8:10])            
            rowdate = datetime(year, month, day)
        elif rollup_type==constants.MONTHLY:            
            rowdate = datetime(year, month, 1)
        return rowdate

    # DAY ROLLUP
    def performDayRollUp(self, metricType, rollup_type, metricTypeRollup, entity_id, condition=""):

#        # To find the date for previous day
#        difference = timedelta(days=-1)
#
#        # To find the date upto which rollup to be done
#        uptoDate = (datetime.utcnow() + difference).strftime("%Y-%m-%d")
#

        today = datetime.utcnow()
        uptoDate = today.strftime("%Y-%m-%d")
        
        # check for default date
        defaultDate = self.insert_rollupstatus_record(entity_id,rollup_type)

        # convirt date string of uptoDate to datetime object using string operations
        year = int(uptoDate[:4])
        month =  int(uptoDate[5:7])
        day = int(uptoDate[8:10])
        formatted_uptoDate = datetime(year, month, day)

        date_format_string = "%Y-%m-%d"
        groupby_format_string = "%Y-%m-%d"
        # fetch rolledup data for given entity_id for given time criteria
        #print rollup_type,"===========",defaultDate,"=========",uptoDate
        resultSet = self.fetch_timebased_rollup_records(date_format_string, groupby_format_string, defaultDate, uptoDate, entity_id, metricType, condition)

        # loop till last record is reached
        while (1):
            row = resultSet.fetchone()
            if row == None:
                break
            else:
                #inser record into rollup table(metrics_arch) for day rollup
                rowdate=self.get_row_date(row,rollup_type)
                self.insert_timebased_rollup_record(row, rowdate, metricTypeRollup, rollup_type, entity_id)
              

        # update timestamp in rollup status table
        self.update_rollupstatus_record(entity_id,formatted_uptoDate,rollup_type)

    
    # MONTH ROLLUP
    def performMonthRollUp(self, metricType, rollup_type, metricTypeRollup, entity_id, condition=""):
#        tempDate = datetime.utcnow()
#        mon = tempDate.month - 1
#        # need to change the year if it's jan of the current year
#        if mon==0:
#            tempDate = datetime.utcnow().replace(month=12).replace(year=(datetime.utcnow().year-1))
#        else:
#            tempDate = (datetime.utcnow().replace(month=(datetime.utcnow().month-1)))
#        uptoDate = tempDate.strftime("%Y-%m")
#
#        year = int(uptoDate[:4])
#        month =  int(uptoDate[5:7])
#        uptoDate = self.last_date_of_previous_month(year, month)

        today = datetime.utcnow()
        uptoDate = date(today.year,today.month,1)
        formatted_uptoDate = uptoDate

        # read defaultDate
        defaultDate = self.insert_rollupstatus_record(entity_id,rollup_type)

        date_format_string = "%Y-%m"
        groupby_format_string = "%Y-%m"
        # fetch rolledup data for given entity_id for given time criteria
        #print rollup_type,"===========",defaultDate,"=========",uptoDate
        resultSet = self.fetch_timebased_rollup_records(date_format_string, groupby_format_string, defaultDate, uptoDate, entity_id, metricType, condition)

        # loop till last record is reached
        while (1):
            row = resultSet.fetchone()
            if row == None:
                break
            else:
                #inser record into rollup table(metrics_arch) for month rollup
                rowdate=self.get_row_date(row,rollup_type)
                self.insert_timebased_rollup_record(row, rowdate, metricTypeRollup, rollup_type, entity_id)

        # update time stamp in rollup_staus table
        self.update_rollupstatus_record(entity_id,formatted_uptoDate,rollup_type) 

    # HOUR ROLLUP
    def performHourRollUp(self, metricType, rollup_type, metricTypeRollup, entity_id, condition=""):

        #uptoDate = self.get_previous_hour()

        today = datetime.utcnow()
        uptoDate = today.strftime("%Y-%m-%d %H")

        # convirt date string of uptoDate to datetime object using string operations
        year = int(uptoDate[:4])
        month =  int(uptoDate[5:7])
        day = int(uptoDate[8:10])
        hour = int(uptoDate[11:13])
        formatted_uptoDate = datetime(year, month, day, hour)

        defaultDate = self.insert_rollupstatus_record(entity_id,rollup_type)

        date_format_string = "%Y-%m-%d %H"
        groupby_format_string = "%Y-%m-%d %H"
        # fetch rolledup data for given entity_id for given time criteria
        #print rollup_type,"===========",defaultDate,"=========",uptoDate
        resultSet = self.fetch_timebased_rollup_records(date_format_string, groupby_format_string, defaultDate, uptoDate, entity_id, metricType, condition)

        # loop till last record is reached
        while (1):
            row = resultSet.fetchone()
            if row == None:
                break
            else:
                #inser record into rollup table(metrics_arch) for month rollup                
                rowdate=self.get_row_date(row,rollup_type)                            
                self.insert_timebased_rollup_record(row, rowdate, metricTypeRollup, rollup_type, entity_id) 

        self.update_rollupstatus_record(entity_id,formatted_uptoDate,rollup_type)

    # WEEKLY ROLLUP
    def performWeekRollUp(self, metricType, rollup_type, metricTypeRollup, entity_id, condition=""):

        # To find the date for last day of the previous week.
        #weekBeforeToDate = self.find_date_for_week_rollup()

        today=datetime.utcnow()
        weekdays=today.weekday()
        weekStartDate=datetime(today.year,today.month,today.day) +timedelta(days=-weekdays)

        uptoDate = weekStartDate.strftime("%Y-%m-%d")

        # convirt date string of uptoDate to datetime object using string operations
        year = int(uptoDate[:4])
        month =  int(uptoDate[5:7])
        day = int(uptoDate[8:10])
        formatted_uptoDate = datetime(year, month, day)

        defaultDate = self.insert_rollupstatus_record(entity_id,rollup_type)

        date_format_string = "%Y-%m-%d"
        groupby_format_string = "%U"
        # fetch rolledup data for given entity_id for given time criteria
        #print rollup_type,"===========",defaultDate,"=========",uptoDate
        resultSet = self.fetch_timebased_rollup_records(date_format_string, groupby_format_string, defaultDate, uptoDate, entity_id, metricType, condition)


        while (1):
            row = resultSet.fetchone()
            if row == None:
                break
            else:
                # insert record into rollup table(metrics_arch) for week rollup
                rowdate=self.get_row_date(row,rollup_type)                
                self.insert_timebased_rollup_record(row, rowdate, metricTypeRollup, rollup_type, entity_id) 

        # update time stamp in rollup status table
        self.update_rollupstatus_record(entity_id,formatted_uptoDate,rollup_type)

    # function not in use currently, created for future use. - not in use at present
    #def insertDataCenterRaw(self, typeMetrics, dict_data, node_id, dc_raw_obj):
        #dc_raw_obj.entity_id = node_id
        #dc_raw_obj.metric_type = metric_type
        #dc_raw_obj.cpu_util=dict_data.get('CPU(%)')
        #dc_raw_obj.mem_util=dict_data.get('MEM(%)')
        #dc_raw_obj.vbds=dict_data.get('VBDS')
        #dc_raw_obj.vbd_oo=dict_data.get('VBD_OO')
        #dc_raw_obj.vbd_rd=dict_data.get('VBD_RD')
        #dc_raw_obj.vbd_wr=dict_data.get('VBD_WR')
        #dc_raw_obj.nets=dict_data.get('NETS')
        #dc_raw_obj.net_tx=dict_data.get('NETTX(k)')
        #dc_raw_obj.net_rx=dict_data.get('NETRX(k)')
        #dc_raw_obj.gb_local = dict_data.get('VM_LOCAL_STORAGE')
        #dc_raw_obj.gb_poolused = dict_data.get('VM_SHARED_STORAGE')
        #dc_raw_obj.gb_pooltotal = dict_data.get('VM_TOTAL_STORAGE')
        #DBSession.add(dc_raw_obj)


    # function not in use currently, created for future use.
    #def insertDataCenterRollup(self, typeMetrics, dict_data, dc_rollup_obj):
        #dc_rollup_obj.metric_type=dict_data.get('metric_type')
        #dc_rollup_obj.rollup_type=dict_data.get('rollup_type')
        #dc_rollup_obj.cdate=dict_data.get('cdate')
        #dc_rollup_obj.cpu_util_avg=dict_data.get('cpu_util_avg')
        #dc_rollup_obj.cpu_util_min=dict_data.get('cpu_util_min')
        #dc_rollup_obj.cpu_util_max=dict_data.get('cpu_util_max')
        #dc_rollup_obj.cpu_util_stddev=dict_data.get('cpu_util_stddev')
        #dc_rollup_obj.mem_util_avg=dict_data.get('mem_util_avg')
        #dc_rollup_obj.mem_util_min=dict_data.get('mem_util_min')
        #dc_rollup_obj.mem_util_max=dict_data.get('mem_util_min')
        #dc_rollup_obj.mem_util_stddev=dict_data.get('mem_util_stddev')
        #dc_rollup_obj.vbds_avg=dict_data.get('vbds_avg')
        #dc_rollup_obj.vbds_min=dict_data.get('vbds_min')
        #dc_rollup_obj.vbds_max=dict_data.get('vbds_max')
        #dc_rollup_obj.vbds_stddev=dict_data.get('vbds_stddev')
        #dc_rollup_obj.vbd_oo_avg=dict_data.get('vbd_oo_avg')
        #dc_rollup_obj.vbd_oo_min=dict_data.get('vbd_oo_min')
        #dc_rollup_obj.vbd_oo_max=dict_data.get('vbd_oo_max')
        #dc_rollup_obj.vbd_oo_stddev=dict_data.get('vbd_oo_stddev')
        #dc_rollup_obj.vbd_rd_avg=dict_data.get('vbd_rd_avg')
        #dc_rollup_obj.vbd_rd_min=dict_data.get('vbd_rd_min')
        #dc_rollup_obj.vbd_rd_max=dict_data.get('vbd_rd_min')
        #dc_rollup_obj.vbd_rd_stddev=dict_data.get('vbd_rd_stddev')
        #dc_rollup_obj.vbd_wr_avg=dict_data.get('vbd_wr_avg')
        #dc_rollup_obj.vbd_wr_min=dict_data.get('vbd_wr_min')
        #dc_rollup_obj.vbd_wr_max=dict_data.get('vbd_wr_max')
        #dc_rollup_obj.vbd_wr_stddev=dict_data.get('vbd_wr_stddev')
        #dc_rollup_obj.nets_avg=dict_data.get('nets_avg')
        #dc_rollup_obj.nets_min=dict_data.get('nets_min')
        #dc_rollup_obj.nets_max=dict_data.get('nets_max')
        #dc_rollup_obj.nets_stddev=dict_data.get('nets_stddev')
        #dc_rollup_obj.net_tx_avg=dict_data.get('net_tx_avg')
        #dc_rollup_obj.net_tx_min=dict_data.get('net_tx_min')
        #dc_rollup_obj.net_tx_max=dict_data.get('net_tx_max')
        #dc_rollup_obj.net_tx_stddev=dict_data.get('net_tx_stddev')
        #dc_rollup_obj.net_rx_avg=dict_data.get('net_rx_avg')
        #dc_rollup_obj.net_rx_min=dict_data.get('net_rx_min')
        #dc_rollup_obj.net_rx_max=dict_data.get('net_rx_max')
        #dc_rollup_obj.net_rx_stddev=dict_data.get('net_rx_stddev')
        #dc_rollup_obj.gb_local_avg=dict_data.get('gb_local_avg')
        #dc_rollup_obj.gb_local_min=dict_data.get('gb_local_min')
        #dc_rollup_obj.gb_local_max=dict_data.get('gb_local_max')
        #dc_rollup_obj.gb_local_stddev=dict_data.get('gb_local_stddev')
        #dc_rollup_obj.gb_poolused_avg=dict_data.get('gb_poolused_avg')
        #dc_rollup_obj.gb_poolused_min=dict_data.get('gb_poolused_min')
        #dc_rollup_obj.gb_poolused_max=dict_data.get('gb_poolused_max')
        #dc_rollup_obj.gb_poolused_stddev=dict_data.get('gb_poolused_stddev')
        #dc_rollup_obj.gb_pooltotal_avg=dict_data.get('gb_pooltotal_avg')
        #dc_rollup_obj.gb_pooltotal_min=dict_data.get('gb_pooltotal_min')
        #dc_rollup_obj.gb_pooltotal_max=dict_data.get('gb_pooltotal_max')
        #dc_rollup_obj.gb_pooltotal_stddev=dict_data.get('gb_pooltotal_stddev')
        #DBSession.add(dc_rollup_obj)


    ## function not in use currently, created for future use.
    #def insertDataCenterCurr(self, typeMetrics, dict_data, node_id, dc_curr_obj):
        #dc_curr_obj.entity_id = node_id
        #dc_curr_obj.metric_type = metric_type
        #dc_curr_obj.cpu_util=dict_data.get('CPU(%)')
        #dc_curr_obj.mem_util=dict_data.get('MEM(%)')
        #dc_curr_obj.vbds=dict_data.get('VBDS')
        #dc_curr_obj.vbd_oo=dict_data.get('VBD_OO')
        #dc_curr_obj.vbd_rd=dict_data.get('VBD_RD')
        #dc_curr_obj.vbd_wr=dict_data.get('VBD_WR')
        #dc_curr_obj.nets=dict_data.get('NETS')
        #dc_curr_obj.net_tx=dict_data.get('NETTX(k)')
        #dc_curr_obj.net_rx=dict_data.get('NETRX(k)')
        #dc_curr_obj.gb_local = dict_data.get('VM_LOCAL_STORAGE')
        #dc_curr_obj.gb_poolused = dict_data.get('VM_SHARED_STORAGE')
        #dc_curr_obj.gb_pooltotal = dict_data.get('VM_TOTAL_STORAGE')
        #dc_curr_obj.cdate=datetime.now()
        #DBSession.add(dc_curr_obj)

    """
    function is created to insert data for SERVER_RAW/SERVER_CURR metrics.
    function will be called only once for updating SERVER_RAW metrics from gridManager
    and in the same call we need to update SERVER_CURR metrics as well
    """     
    def insertServerMetricsData(self, dict_data, node_id, metrics_obj):
        strt = p_task_timing_start(MTR_LOGGER, "InsertServerMetrics", node_id, log_level="DEBUG")
        # create a list of metrics_types to be updated
        metric_type_list = [constants.SERVER_RAW, constants.SERVER_CURR]
        # loop to update VM_CURR and VM_RAW metrics
        for metric_type in metric_type_list:
            # delete previous entry for the passed node_id from VM_CURR metrics
            if metric_type == constants.SERVER_CURR:
                metrics_obj = MetricServerCurr()
                try:
                    self.DeleteCurrentMetrics(constants.SERVER_CURR, node_id)
                except Exception, ex:
                    LOGGER.error(to_str(ex))
                    LOGGER.debug('Failed: insertServerMetricsData')
                    raise

            # to retrive the integer from string '1024k'
            server_mem = dict_data.get('SERVER_MEM')
            if server_mem:
                server_mem = float(server_mem[:-1])
            server_cpus=dict_data.get('SERVER_CPUs')
            #to retrive the integer from string '2 @ 1864MHz'
            if server_cpus:
                server_cpus = int(server_cpus.split(' ')[0])
            metrics_obj.entity_id = node_id
            metrics_obj.metric_type = metric_type
            metrics_obj.cpu_util=dict_data.get('VM_TOTAL_CPU(%)',0.00)
            metrics_obj.mem_util=dict_data.get('VM_TOTAL_MEM(%)',0.00)
            metrics_obj.vbds=dict_data.get('VM_TOTAL_VBDS')
            metrics_obj.vbd_oo=dict_data.get('VM_TOTAL_VBD_OO')
            metrics_obj.vbd_rd=dict_data.get('VM_TOTAL_VBD_RD')
            metrics_obj.vbd_wr=dict_data.get('VM_TOTAL_VBD_WR')
            metrics_obj.nets=dict_data.get('VM_TOTAL_NETS')
            metrics_obj.net_tx=dict_data.get('VM_TOTAL_NETTX(k)')
            metrics_obj.net_rx=dict_data.get('VM_TOTAL_NETRX(k)')
            metrics_obj.gb_local = dict_data.get('VM_LOCAL_STORAGE',0.00)
            metrics_obj.gb_poolused = dict_data.get('VM_SHARED_STORAGE',0.00)
            metrics_obj.gb_pooltotal = dict_data.get('VM_TOTAL_STORAGE',0.00)
            metrics_obj.cdate=datetime.utcnow()
            metrics_obj.state=to_unicode(dict_data.get('NODE_STATUS'))
            metrics_obj.paused_vms=dict_data.get('PAUSED_VMs',0)
            metrics_obj.running_vms=dict_data.get('RUNNING_VMs',0)
            metrics_obj.crahsed_vms=dict_data.get('CRASHED_VMs',0)
            metrics_obj.total_mem=dict_data.get('VM_TOTAL_MEM',0.000)
            metrics_obj.total_cpu=dict_data.get('VM_TOTAL_CPU',0)
            metrics_obj.total_vms=dict_data.get('TOTAL_VMs',0)
            metrics_obj.server_cpus=server_cpus
            metrics_obj.server_mem=server_mem
            metrics_obj.host_mem=dict_data.get('HOST_MEM(%)',0.00)
            metrics_obj.host_cpu=dict_data.get('HOST_CPU(%)',0.00)
            DBSession.add(metrics_obj)
        p_task_timing_end(MTR_LOGGER, strt)


    """
    insert data in SERVERPOOL_RAW metrics. This data is rolled-up
    data from SERVER_RAW metrics table and passed to this function as dict
    """
    def insertServerPoolMetricsData(self, dict_data, node_id, metrics_obj):
        strt = p_task_timing_start(MTR_LOGGER, "InsertServerPoolMetrics", node_id, log_level="DEBUG")
        metric_type_list = [constants.SERVERPOOL_RAW, constants.SERVERPOOL_CURR]
        # loop to update VM_CURR and VM_RAW metrics 
        for metric_type in metric_type_list:
            # delete previous entry for the passed node_id from VM_CURR metrics
            if metric_type == constants.SERVERPOOL_CURR:
                metrics_obj = ServerPoolCurr()
                try:
                    self.DeleteCurrentMetrics(constants.SERVERPOOL_CURR, node_id)
                except Exception, ex:
                    LOGGER.error(to_str(ex))
                    LOGGER.debug('Failed: insertServerPoolMetricsData')
                    raise
            metrics_obj.entity_id = node_id
            metrics_obj.metric_type = metric_type
            metrics_obj.cpu_util=dict_data.get('VM_TOTAL_CPU(%)',0.00)
            metrics_obj.mem_util=dict_data.get('VM_TOTAL_MEM(%)',0.00)
            metrics_obj.vbds=dict_data.get('VM_TOTAL_VBDS')
            metrics_obj.vbd_oo=dict_data.get('VM_TOTAL_VBD_OO')
            metrics_obj.vbd_rd=dict_data.get('VM_TOTAL_VBD_RD')
            metrics_obj.vbd_wr=dict_data.get('VM_TOTAL_VBD_WR')
            metrics_obj.nets=dict_data.get('VM_TOTAL_NETS')
            metrics_obj.net_tx=dict_data.get('VM_TOTAL_NETTX(k)')
            metrics_obj.net_rx=dict_data.get('VM_TOTAL_NETRX(k)')
            metrics_obj.gb_local = dict_data.get('VM_LOCAL_STORAGE',0.00)
            metrics_obj.gb_poolused = dict_data.get('VM_SHARED_STORAGE',0.00)
            metrics_obj.gb_pooltotal = dict_data.get('VM_TOTAL_STORAGE',0.00)
            metrics_obj.cdate=datetime.utcnow()
            metrics_obj.paused_vms=dict_data.get('PAUSED_VMs',0)
            metrics_obj.running_vms=dict_data.get('RUNNING_VMs',0)
            metrics_obj.crahsed_vms=dict_data.get('CRASHED_VMs',0)
            metrics_obj.total_mem=dict_data.get('VM_TOTAL_MEM',0.00)
            metrics_obj.total_cpu=dict_data.get('VM_TOTAL_CPU',0)
            metrics_obj.server_mem=dict_data.get('SERVER_MEM',0.00)
            metrics_obj.server_cpus=dict_data.get('SERVER_CPUs',0)
            metrics_obj.total_vms=dict_data.get('TOTAL_VMs',0)
            metrics_obj.server_count=dict_data.get('server_count',0)
            metrics_obj.nodes_connected=dict_data.get('NODES_CONNECTED',0)
            DBSession.add(metrics_obj)
            p_task_timing_end(MTR_LOGGER, strt)


    """
    function is modified to insert data for VM_CURR and VM_RAW metrics.
    function will be called only once for updating VM_RAW metrics from GridManager
    and in the same call we need to update VM_CURR metrics as well
    """ 
    def insertMetricsData(self, dict_data, node_id, metrics_obj):
        # create a list of metrics_types to be updated
        metric_type_list = [constants.VM_RAW, constants.VM_CURR]
        strt = p_task_timing_start(MTR_LOGGER, "InsertVMMetrics", node_id, log_level="DEBUG")
        # loop to update VM_CURR and VM_RAW metrics 
        for metric_type in metric_type_list:
            # delete previous entry for the passed node_id from VM_CURR metrics
            if metric_type == constants.VM_CURR:
                metrics_obj = MetricVMCurr()
                try:
                    self.DeleteCurrentMetrics(constants.VM_CURR, node_id)
                except Exception, ex:
                    LOGGER.error(to_str(ex))
                    LOGGER.debug('Failed: insertMetricsData')
                    raise
            ###commented on 25/11/09
#            vm = DBSession.query(VM).filter(VM.id==node_id).first()
#            if vm:
#                state = vm.get_state()
#            metrics_obj.state=state
            metrics_obj.state=to_unicode(dict_data.get('STATE'))
            ###end
            metrics_obj.entity_id = node_id
            metrics_obj.metric_type = metric_type
            metrics_obj.cpu_util=dict_data.get('CPU(%)',0)
            metrics_obj.vm_cpu_util=dict_data.get('VM_CPU(%)',0)
            metrics_obj.mem_util=dict_data.get('MEM(%)',0)
            metrics_obj.vbds=dict_data.get('VBDS',0)
            metrics_obj.vbd_oo=dict_data.get('VBD_OO',0)
            metrics_obj.vbd_rd=dict_data.get('VBD_RD',0)
            metrics_obj.vbd_wr=dict_data.get('VBD_WR',0)
            metrics_obj.nets=dict_data.get('NETS',0)
            metrics_obj.net_tx=dict_data.get('NETTX(k)',0)
            metrics_obj.net_rx=dict_data.get('NETRX(k)',0)
            metrics_obj.gb_local = dict_data.get('VM_LOCAL_STORAGE',0)
            metrics_obj.gb_poolused = dict_data.get('VM_SHARED_STORAGE',0)
            metrics_obj.gb_pooltotal = dict_data.get('VM_TOTAL_STORAGE',0)
            metrics_obj.cdate=datetime.utcnow()
            DBSession.add(metrics_obj)
        p_task_timing_end(MTR_LOGGER, strt)


    def timebasis_rollup_for_all_nodes(self, auth):
        serverpool_ents = auth.get_entities(to_unicode(constants.SERVER_POOL))
        #initialize metric_type value for rollup/raw table to be used in the function
        for each_serverpool in serverpool_ents:
            metric_type_raw = constants.SERVERPOOL_RAW
            metric_type_rollup = constants.SERVERPOOL_ROLLUP
            #timebasis rollup at the server pool level from metrics table
            self.performHourRollUp(metric_type_raw, constants.HOURLY,metric_type_rollup, each_serverpool.entity_id)
            self.performDayRollUp(metric_type_raw, constants.DAILY,metric_type_rollup, each_serverpool.entity_id)
            self.performWeekRollUp(metric_type_raw, constants.WEEKLY,metric_type_rollup, each_serverpool.entity_id)
            self.performMonthRollUp(metric_type_raw, constants.MONTHLY,metric_type_rollup, each_serverpool.entity_id)
            try:
                # retrive serverpool entity
                serverpool_ent=auth.get_entity(each_serverpool.entity_id)
                # retrieve all server entities inside a current pool 
                server_ents=auth.get_entities(to_unicode(constants.MANAGED_NODE),parent=serverpool_ent)
                # loop through all the servers present in the current serverpool
                for each_server in server_ents:
                    metric_type_raw = constants.SERVER_RAW
                    metric_type_rollup = constants.SERVER_ROLLUP
                    # timebasis rollup at the server level from metrics table
                    self.performHourRollUp(metric_type_raw, constants.HOURLY,metric_type_rollup, each_server.entity_id)
                    self.performDayRollUp(metric_type_raw, constants.DAILY, metric_type_rollup, each_server.entity_id)
                    self.performWeekRollUp(metric_type_raw, constants.WEEKLY, metric_type_rollup,  each_server.entity_id)
                    self.performMonthRollUp(metric_type_raw, constants.MONTHLY, metric_type_rollup, each_server.entity_id)

                    #loop through all the vms inside the current managed node
                    vm_ent=auth.get_entity(each_server.entity_id)
                    vms = auth.get_entities(to_unicode(constants.DOMAIN), parent=vm_ent)
                    for each_vm in vms:
                        metric_type_raw = constants.VM_RAW
                        metric_type_rollup = constants.VM_ROLLUP        
                        # timebasis rollup at the VM level from metrics table
                        condition = " and state != "+to_str(VM.SHUTDOWN)+" "
                        self.performHourRollUp(metric_type_raw, constants.HOURLY, metric_type_rollup, each_vm.entity_id, condition )
                        self.performDayRollUp(metric_type_raw, constants.DAILY, metric_type_rollup, each_vm.entity_id, condition)
                        self.performWeekRollUp(metric_type_raw, constants.WEEKLY, metric_type_rollup, each_vm.entity_id, condition)
                        self.performMonthRollUp(metric_type_raw, constants.MONTHLY, metric_type_rollup, each_vm.entity_id, condition)

            except Exception, ex:
                LOGGER.error(to_str(ex))
                LOGGER.debug('Failed: timebasis_rollup_for_all_nodes')
                raise

    def insert_into_purge_config(self, entity_id, data_type, retention_days):
        obj_purge_config = PurgeConfiguration()
        obj_purge_config.entity_id = entity_id
        obj_purge_config.data_type = data_type
        obj_purge_config.retention_days = retention_days
        DBSession.add(obj_purge_config)

    """
    calling a function to creatlist of tuples which has data_type(HOURLY..etc) and criteria 
    as shown below...
    purge_config_data = [(data_type, purge_before_date), (data_type, purge_before_date),
    (data_type, purge_before_date), (data_type, purge_before_date), 
    (data_type, purge_before_date)] for every entity_id.
    """
    def get_purgeconfig_data(self, purge_day_data, purge_hr_data, purge_week_data, purge_month_data, purge_raw_data):
        purge_config_data = []
        individual_config_data = []
        
        todays_date = datetime.utcnow()

        # Calculate datetime for the time window entry for Day 
        time_diff = timedelta(days=-int(purge_day_data))
        purge_before_date = (todays_date + time_diff).strftime("%Y-%m-%d")
        formatted_uptoDate = datetime(int(purge_before_date[:4]), int(purge_before_date[5:7]), int(purge_before_date[8:10]))
        #date_format = '%Y-%m-%d'
        data_type = constants.DAILY
        individual_config_data.append(data_type)
        individual_config_data.append(formatted_uptoDate)
        purge_config_data.append(individual_config_data)

        # Calculate datetime for the time window entry for Hour
        individual_config_data = []
        time_diff = timedelta(days=-int(purge_hr_data))
        purge_before_date = (todays_date + time_diff).strftime("%Y-%m-%d %H")
        formatted_uptoDate = datetime(int(purge_before_date[:4]), int(purge_before_date[5:7]), int(purge_before_date[8:10]), int(purge_before_date[11:13]))
        #date_format = '%Y-%m-%d %H'
        data_type = constants.HOURLY
        individual_config_data.append(data_type)
        individual_config_data.append(formatted_uptoDate)
        purge_config_data.append(individual_config_data)

        # Calculate datetime for the time window entry for Weeks
        individual_config_data = []
        time_diff = timedelta(days=-int(purge_week_data))
        purge_before_date = (todays_date + time_diff).strftime("%Y-%m-%d")
        formatted_uptoDate = datetime(int(purge_before_date[:4]), int(purge_before_date[5:7]), int(purge_before_date[8:10]))            
        data_type = constants.WEEKLY
        individual_config_data.append(data_type)
        individual_config_data.append(formatted_uptoDate)
        purge_config_data.append(individual_config_data)

        # Calculate datetime for the time window entry for Months
        individual_config_data = []
        # diff calculation is done using days delta function,since 'purge_month_data' value is in days
        time_diff = timedelta(days=-int(purge_month_data))
        purge_before_date = (todays_date + time_diff).strftime("%Y-%m")            
        formatted_uptoDate = datetime(int(purge_before_date[:4]), int(purge_before_date[5:7]), 1)            
        data_type = constants.MONTHLY
        individual_config_data.append(data_type)
        individual_config_data.append(formatted_uptoDate)
        purge_config_data.append(individual_config_data)

        #Calculate datetime for the time window entry for RAW table
        #for raw calculations (assuming time window is entered in no of days)
        individual_config_data = []
        time_diff = timedelta(days=-int(purge_raw_data))
        purge_before_date = (todays_date + time_diff).strftime("%Y-%m-%d")
        formatted_uptoDate = datetime(int(purge_before_date[:4]), int(purge_before_date[5:7]), int(purge_before_date[8:10]))                        
        data_type = constants.RAW
        individual_config_data.append(data_type)
        individual_config_data.append(formatted_uptoDate)
        purge_config_data.append(individual_config_data)
        return purge_config_data

    """
    function implemented to purge all the Serverpools/servers/vms raw data as well as rollup data for VM from metrics and metrics_arch table. This is the thread function invoked to purge the
    data at the preconfigured interval. It is executed as repeating task 
    """
    def purging_for_all_nodes(self, auth):
        serverpool_ents = auth.get_entities(to_unicode(constants.SERVER_POOL))
        for serverpool_ids in serverpool_ents:
            #purging at the pool level
            self.purging(serverpool_ids.entity_id) 
            # retrive serverpool entity
            try:
                serverpool_ent=auth.get_entity(serverpool_ids.entity_id)
                server_ents=auth.get_entities(to_unicode(constants.MANAGED_NODE),parent=serverpool_ent)
                #loop through all the servers present in the current serverpool
                for server_id in server_ents:
                    #purge rolled-up data for metric_type SERVER_RAW from metrics table
                    self.purging(server_id.entity_id)
                    #to find the vms inside the current managed node
                    vm_ent=auth.get_entity(server_id.entity_id)
                    vms = auth.get_entities(to_unicode(constants.DOMAIN), parent=vm_ent)
                    for each_vm in vms:
                        # for each VM data to be purged for VM_RAW/VM_ROLLUP metrics_type
                        vmId = each_vm.entity_id
                        self.purging(vmId)
            except Exception, ex:
                LOGGER.error(to_str(ex))
                LOGGER.debug('Failed: purging_for_all_nodes')
                raise

    def purging(self, entity_id):
        # Read development.ini file to get the default individual_config_data entered 
        purge_hr_data = tg.config.get('purge_hr_data', 0)
        purge_day_data = tg.config.get('purge_day_data', 0)
        purge_week_data = tg.config.get('purge_week_data', 0)
        purge_month_data = tg.config.get('purge_month_data', 0)
        purge_raw_data = tg.config.get('purge_raw_data', 0)
        # fetch time criteria for purging for the given entity id from database table
        resultSet = DBSession.query(PurgeConfiguration.data_type, PurgeConfiguration.retention_days).filter(PurgeConfiguration.entity_id==entity_id).all()
        #if database doesn't have entry for the given entity id
        if not resultSet:
            purge_config_data = self.get_purgeconfig_data(purge_day_data, purge_hr_data, purge_week_data, purge_month_data, purge_raw_data)
            # make a entry into purge_config database table
            purge_config_dict= {constants.HOURLY:purge_hr_data, constants.DAILY:purge_day_data, constants.WEEKLY:purge_week_data, constants.MONTHLY:purge_month_data, constants.RAW:purge_raw_data}
            for keys in purge_config_dict:
                self.insert_into_purge_config(entity_id, keys, purge_config_dict[keys])
        else: #read purge configuration values from database table
            for individual_config_data in resultSet:
                individual_config_data = list(individual_config_data)
                purge_type = individual_config_data[PURGE_TYPE]
                purge_date = individual_config_data[PURGE_DATE]
                
                if purge_type==constants.DAILY:
                    purge_day_data = purge_date
                elif purge_type==constants.HOURLY:
                    purge_hr_data = purge_date
                elif purge_type==constants.WEEKLY:
                    purge_week_data = purge_date
                elif purge_type==constants.MONTHLY:
                    purge_month_data = purge_date
                else:
                    purge_raw_data = purge_date
                purge_config_data = self.get_purgeconfig_data(purge_day_data, purge_hr_data, purge_week_data,  purge_month_data, purge_raw_data)
        """
        loop through all purge_config_data returned from purge_configuration
        for (data_type, purge_before_date)
        """
        for individual_config_data in purge_config_data:
            if individual_config_data: # (data_type, purge_before_date)
                purge_type = individual_config_data[PURGE_TYPE]
                if purge_type==constants.RAW: # purge VM_RAW entries
                        """
                        purge the all the data from metrics table for date less than and 
                        equal to purge_before_date 
                        """
                        try:
                            try:
                                #DBSession.query(Metrics).filter(Metrics.entity_id==entity_id).filter(Metrics.cdate <= individual_config_data[PURGE_DATE]).delete()
                                LockManager().get_lock(constants.METRICS,entity_id, constants.PURGE_METRICS, constants.Table_metrics)
                                xs=DBSession.query(Metrics).filter(Metrics.entity_id==entity_id).filter(Metrics.cdate <= individual_config_data[PURGE_DATE]).all()
                                for x in xs:
                                    DBSession.delete(x)
                            except Exception, ex:
                                LOGGER.error(to_str(ex))
                                LOGGER.debug('Failed: purging')
                                raise
                        finally:
                            LockManager().release_lock()

                else: # purge ROLLUP table entries
                        """
                        purge the all the data from MetricsArch table for date less than and 
                        equal to purge_before_date and rollup_type = HOURLY/WEEKLY..etc
                        """
                        try:
                            try:
                                #DBSession.query(MetricsArch).filter(MetricsArch.entity_id==entity_id).filter(MetricsArch.rollup_type==individual_config_data[PURGE_TYPE]).filter(MetricsArch.cdate <= individual_config_data[PURGE_DATE]).delete()
                                LockManager().get_lock(constants.METRICS,entity_id, constants.PURGE_METRICS, constants.Table_metrics_arch)
                                xs=DBSession.query(MetricsArch).filter(MetricsArch.entity_id==entity_id).filter(MetricsArch.rollup_type==individual_config_data[PURGE_TYPE]).filter(MetricsArch.cdate <= individual_config_data[PURGE_DATE]).all()
                                for x in xs:
                                    DBSession.delete(x)

                            except Exception, ex:
                                LOGGER.error(to_str(ex))
                                LOGGER.debug('Failed: purging')
                                raise
                        finally:
                            LockManager().release_lock()

    def getVMCurrMetricsData(self, metric_type, node_id, auth):
        class_name = self.getClassfromMetricType(metric_type)
        currVMMetricsData = None
        try:
            currVMMetricsData = DBSession.query(class_name).filter(class_name.entity_id==node_id.entity_id).filter(class_name.metric_type==metric_type).first()
        except Exception, ex:
            LOGGER.error(to_str(ex))
            LOGGER.debug('Failed: getVMCurrMetricsData')
            raise
        return currVMMetricsData
    
    """
    function returns list of metrics data for passed metric_type and node_id. It is created for
    SERVER_RAW/SERVER_CURR
    """
    def getServerCurrMetricsData(self, metric_type, node_id):
        class_name = self.getClassfromMetricType(metric_type)
        currMetricsData = None
        try:
            currMetricsData = DBSession.query(class_name).filter(class_name.entity_id==node_id).filter(class_name.metric_type==metric_type).first()
        except Exception, ex:
            LOGGER.error(to_str(ex))
            LOGGER.debug('Failed: getServerCurrMetricsData')
            raise
        
        return currMetricsData

    def getServerMetrics(self,node_id,hrs):
        metric_type=constants.SERVER_ROLLUP
        to_date=datetime.utcnow()

        if hrs is None or hrs==0 or hrs==1:
            metric_type=constants.SERVER_RAW
            hrs=1
        
        class_name = self.getClassfromMetricType(metric_type)

        if metric_type == constants.SERVER_ROLLUP:
            col1=class_name.cpu_util_avg
            col2=class_name.mem_util_avg            
        elif  metric_type == constants.SERVER_RAW:
            col1=class_name.cpu_util
            col2=class_name.mem_util

        from_date=to_date+timedelta(seconds=-(hrs*60*60))
        
        query=DBSession.query(func.sum(col1)/func.count(col1),func.sum(col2)/func.count(col2),class_name.entity_id, class_name.cdate).\
                filter(class_name.entity_id==node_id).\
                filter(class_name.metric_type==metric_type).\
                filter(class_name.cdate>=from_date).\
                filter(class_name.cdate<=to_date)

        query=query.group_by(class_name.entity_id)
        rawList=query.first()        
        metrics={}
        metrics['VM_TOTAL_CPU(%)']=0.0
        metrics['VM_TOTAL_MEM(%)']=0.0
        if rawList is not None:
            rawData = list(rawList)
            metrics['VM_TOTAL_CPU(%)']=rawData[0]
            metrics['VM_TOTAL_MEM(%)']=rawData[1]            
        return metrics

    """
    function returns list of metrics data for passed metric_type,from_date and to_date. It is
    created for VM_RAW table
    """
    def getRawData(self, entity_id, metric_type, from_date, to_date):
        class_name = self.getClassfromMetricType(metric_type)
        raw_data_list = []
        for rawData in DBSession.query(class_name.cpu_util, class_name.mem_util, class_name.vbds, class_name.vbd_oo, class_name.vbd_rd, class_name.vbd_wr, class_name.nets, class_name.nets_tx, class_name.nets_rx, class_name.gb_local, class_name.gb_poolused, class_name.gb_pooltotal, class_name.state, class_name.metric_type, class_name.cdate).filter(class_name.entity_id==entity_id).filter(class_name.metric_type==metric_type).filter(class_name.cdate>=from_date).filter(class_name.cdate<=to_date).all():
            rawDataList = list(rawData)
            raw_data_list.append(rawDataList)
        return raw_data_list

    def getRawMetricData(self, entity_ids, metric,metric_type, from_date, to_date):
        class_name = self.getClassfromMetricType(metric_type)
        raw_data_list = []
        
        col=self.getMetricCol(metric,metric_type,class_name)

        for rawData in DBSession.query(col,class_name.cdate).filter(class_name.entity_id.in_(entity_ids)).\
            filter(class_name.metric_type==metric_type).filter(class_name.cdate>=from_date).\
            filter(class_name.cdate<=to_date).all():
            rawDataList = list(rawData)
            raw_data_list.append(rawDataList)
        return raw_data_list 

    def getRawTopMetric(self, entity_ids, metric, metric_type, \
                                from_date, to_date, order="DESC", limit=5):
        class_name = self.getClassfromMetricType(metric_type)
        raw_data_list = []

        col=self.getMetricCol(metric,metric_type,class_name)
        
        query=DBSession.query((func.sum(col)/func.count(col)).label("usge"),class_name.entity_id, class_name.cdate).\
                filter(class_name.entity_id.in_(entity_ids)).\
                filter(class_name.metric_type==metric_type).\
                filter(class_name.cdate>=from_date).\
                filter(class_name.cdate<=to_date)

        query=query.group_by(class_name.entity_id)
        query=query.order_by("usge "+order)
        query=query.limit(limit)
        
        rawList=query.all()        
        for rawData in rawList:
            rawDataList = list(rawData)
            raw_data_list.append(rawDataList)
        return raw_data_list

    def getRawAvg(self,entity_id, entity_type, metric, metric_type, from_date, to_date):
        class_name = self.getClassfromMetricType(metric_type)

        col=self.getMetricCol(metric,metric_type,class_name)

        avg=0.0
        fquery = DBSession.query(func.avg(col)).\
                    filter(class_name.entity_id==entity_id).filter(class_name.metric_type==metric_type).\
                    filter(class_name.cdate>=from_date).filter(class_name.cdate<=to_date)
       
        if entity_type==constants.DOMAIN:          
            fquery=fquery.filter(class_name.state != VM.SHUTDOWN)
        dataList=fquery.group_by(class_name.entity_id).all()
        
        if len(dataList) >0:
            avg=dataList[0][0]
        return avg

    """
    function returns list of metrics data for passed metric_type and pool_id. It is
    created for ServerPool CURR/RAW metrics.
    """
    def getServerPoolCurrMetricsData(self, pool_id, metric_type):
        class_name = self.getClassfromMetricType(metric_type)
        rawDataList = []
        currMetricsData = None
        try:
            currMetricsData = DBSession.query(class_name).filter(class_name.entity_id==pool_id).filter(class_name.metric_type==metric_type).first()
        except Exception, ex:
            LOGGER.error(to_str(ex))
            LOGGER.debug('Failed: getServerPoolCurrMetricsData')
            raise

        return currMetricsData

    """
    function returns list of metrics data for passed metric_type,from_date and to_date. It is
    created for ROLLUP tables
    """
    def getRollupData(self,entity_id, metric_type, from_date, to_date): 
        class_name = self.getClassfromMetricType(metric_type)
        raw_data_list = []
        for rolupData in DBSession.query(class_name.state, class_name.metric_type, class_name.rollup_type, class_name.cdate, class_name.cpu_util_avg, class_name.cpu_util_min, class_name.cpu_util_max, class_name.cpu_util_stddev, class_name.mem_util_avg, class_name.mem_util_min, class_name.mem_util_min, class_name.mem_util_stddev, class_name.vbds_avg, class_name.vbds_min, class_name.vbds_max, class_name.vbds_stddev, class_name.vbd_oo_av, class_name.vbd_oo_min, class_name.vbd_oo_max, class_name.vbd_oo_stddev, class_name.vbd_rd_avg, class_name.vbd_rd_min, class_name.vbd_rd_min, class_name.vbd_rd_stddev, class_name.vbd_wr_avg, class_name.vbd_wr_min, class_name.vbd_wr_max, class_name.vbd_wr_stddev, class_name.nets_avg, class_name.nets_min, class_name.nets_max, class_name.nets_stddev, class_name.net_tx_avg, class_name.net_tx_min, class_name.net_tx_max, class_name.net_tx_stddev, class_name.net_rx_avg, class_name.net_rx_min, class_name.net_rx_max, class_name.net_rx_stddev, class_name.gb_local_avg, class_name.gb_local_min, class_name.gb_local_max, class_name.gb_local_stddev, class_name.gb_poolused_avg, class_name.gb_poolused_min, class_name.gb_poolused_max, class_name.gb_poolused_stddev, class_name.gb_pooltotal_avg, class_name.gb_pooltotal_min, class_name.gb_pooltotal_max, class_name.gb_pooltotal_stddev, class_name.entity_id).filter(class_name.entity_id==entity_id).filter(class_name.metric_type==metric_type).filter(class_name.cdate>=from_date).filter(class_name.cdate<=to_date).all():
            rollupDataList = list(rolupData)
            raw_data_list.append(rollupDataList)
        return raw_data_list


    def getRollupMetricData(self, entity_ids, metric, metric_type, rollup_type,\
                                from_date, to_date):
        class_name = self.getClassfromMetricType(metric_type)
        data_list = []
        
        col=self.getMetricCol(metric,metric_type,class_name)

        for data in DBSession.query(col, class_name.cdate, \
                    class_name.metric_type, class_name.rollup_type, class_name.entity_id).\
                    filter(class_name.entity_id.in_(entity_ids)).filter(class_name.metric_type==metric_type).\
                    filter(class_name.rollup_type==rollup_type).filter(class_name.cdate>=from_date).\
                    filter(class_name.cdate<=to_date).all():
            dataList = list(data)
            data_list.append(dataList)
        return data_list

    def getRollupAvg(self, entity_id, metric, metric_type, rollup_type,\
                                from_date, to_date):
        class_name = self.getClassfromMetricType(metric_type)
                
        col=self.getMetricCol(metric,metric_type,class_name)
        
        avg=0.0
        dataList = DBSession.query(func.avg(col)).\
                    filter(class_name.entity_id==entity_id).filter(class_name.metric_type==metric_type).\
                    filter(class_name.rollup_type==rollup_type).filter(class_name.cdate>=from_date).\
                    filter(class_name.cdate<=to_date).group_by(class_name.entity_id).all()
        
        if len(dataList) >0:
            avg=dataList[0][0]
        return avg

    def getRollupTop(self, entity_ids, metric, metric_type, rollup_type,\
                                from_date, to_date, order="DESC", limit=5):
        class_name = self.getClassfromMetricType(metric_type)
        data_list = []
            
        col=self.getMetricCol(metric,metric_type,class_name)

        query=DBSession.query((func.sum(col)/func.count(col)).label('usge'), class_name.entity_id).\
                    filter(class_name.entity_id.in_(entity_ids)).filter(class_name.metric_type==metric_type).\
                    filter(class_name.rollup_type==rollup_type).filter(class_name.cdate>=from_date).\
                    filter(class_name.cdate<=to_date)

        query=query.group_by(class_name.entity_id)
        query=query.order_by("usge "+order)
        query=query.limit(limit)
        
        for data in query.all():
            dataList = list(data)
            data_list.append(dataList)
        return data_list
    
    def getCurrentTopMetricData(self, entity_ids, metric, metric_type, order="DESC",limit=5):
        class_name = self.getClassfromMetricType(metric_type)
        data_list = []
        
        col=self.getMetricCol(metric,metric_type,class_name)
        
        query=DBSession.query(col, class_name.entity_id, class_name.metric_type).\
                                filter(class_name.metric_type==metric_type)
        query=query.filter(class_name.entity_id.in_(entity_ids))
        if order=='ASC':
            query=query.order_by(col.asc())
        else:
            query=query.order_by(col.desc())
        query=query.limit(limit)
        
        for data in query.all():
            dataList = list(data)
            data_list.append(dataList)
        return data_list

    def getMetricCol(self,metric,metric_type,class_name):
        if metric==constants.METRIC_CPU:
            if metric_type in [constants.SERVER_RAW,constants.SERVER_CURR]:
                col=class_name.host_cpu
            elif metric_type in [constants.SERVER_ROLLUP]:
                col=class_name.host_cpu_avg
            elif metric_type in [constants.VM_RAW,constants.VM_CURR,\
                            constants.SERVERPOOL_RAW,constants.SERVERPOOL_CURR,\
                            constants.DATACENTER_RAW,constants.DATACENTER_CURR]:
                col=class_name.cpu_util
            elif metric_type in [constants.VM_ROLLUP,constants.SERVERPOOL_ROLLUP,constants.DATACENTER_ROLLUP]:
                col=class_name.cpu_util_avg
        elif metric==constants.METRIC_VMCPU:
            if metric_type in [constants.VM_RAW,constants.VM_CURR]:
                col=class_name.vm_cpu_util
            elif metric_type in [constants.VM_ROLLUP]:
                col=class_name.vm_cpu_util_avg
        elif metric==constants.METRIC_MEM:
            if metric_type in [constants.SERVER_RAW,constants.SERVER_CURR]:
                col=class_name.host_mem
            elif metric_type in [constants.SERVER_ROLLUP]:
                col=class_name.host_mem_avg
            elif metric_type in [constants.VM_RAW,constants.VM_CURR,\
                            constants.SERVERPOOL_RAW,constants.SERVERPOOL_CURR,\
                            constants.DATACENTER_RAW,constants.DATACENTER_CURR]:
                col=class_name.mem_util
            elif metric_type in [constants.VM_ROLLUP,constants.SERVERPOOL_ROLLUP,constants.DATACENTER_ROLLUP]:
                col=class_name.mem_util_avg
        return col

    """
    function to create serverpool metrics from server_raw table. function implementation is similar
    to gather_info_for_pool. This function calculates the metrics by summing up all the
    available server's data for given serverpool id.
    """
    def collect_serverpool_metrics(self, serverpool_id,connected, auth):
        strt = p_task_timing_start(MTR_LOGGER, "CollectServerPoolMetrics", serverpool_id)
        server_dict = {}
        # get the server ids list from the serverpool id 
        serverpool_ent =auth.get_entity(serverpool_id)
        managed_nodes=auth.get_entities(to_unicode(constants.MANAGED_NODE),parent=serverpool_ent)
        if managed_nodes:
            # sql to find sum of required colums of server metrics to create server pool metrics. 
            sql = 'select sum(fcol1), sum(fcol2), sum(icol1), sum(icol2), sum(icol3), sum(icol4), sum(icol5), sum(icol6), sum(icol7), sum(fcol3), sum(fcol4), sum(fcol5), sum(icol8), sum(icol9), sum(icol10), sum(icol11), sum(icol12), sum(fcol6), sum(fcol7), sum(fcol8), count(fcol8) from metrics_curr where metric_type = %s and entity_id in (' % constants.SERVER_CURR
            for node in managed_nodes: 
                sql+= ' "%s", ' % (node.entity_id)
            sql = sql[:-2]
            sql+= ')'
            resultSet = DBSession.execute(sql)
            record = resultSet.fetchone()
            server_dict['VM_TOTAL_CPU(%)'] = record[0]
            server_dict['VM_TOTAL_MEM(%)'] = record[1]
            server_dict['VM_TOTAL_VBDS'] = record[2]
            server_dict['VM_TOTAL_VBD_OO'] = record[3]
            server_dict['VM_TOTAL_VBD_RD'] = record[4]
            server_dict['VM_TOTAL_VBD_WR'] = record[5]
            server_dict['VM_TOTAL_NETS'] = record[6]
            server_dict['VM_TOTAL_NETTX(k)'] = record[7]
            server_dict['VM_TOTAL_NETRX(k)'] = record[8]
            server_dict['VM_LOCAL_STORAGE'] = record[9]
            server_dict['VM_SHARED_STORAGE'] = record[10]
            server_dict['VM_TOTAL_STORAGE'] = record[11]
            server_dict['TOTAL_VMs'] = record[12]
            server_dict['PAUSED_VMs']=record[13]
            server_dict['RUNNING_VMs']=record[14]
            server_dict['SERVER_CPUs']=record[15]
            server_dict['CRASHED_VMs']=record[16]
            server_dict['VM_TOTAL_MEM']=record[17]
            server_dict['VM_TOTAL_CPU']=record[18]
            server_dict['SERVER_MEM']=record[19]
            server_dict['entity_id']=serverpool_id
            server_dict['metric_type']=constants.SERVERPOOL_RAW
            server_dict['cdate']=datetime.utcnow()
            server_dict['server_count']=record[20]
            server_dict['NODE_TYPE'] = 'SERVER_POOL'
            server_dict['NODES_CONNECTED'] = connected

            metrics_obj = ServerPoolRaw()
            # Insert the rolled-up server metrics into serverpool metrics curr and raw tables
            self.insertServerPoolMetricsData(server_dict, serverpool_id, metrics_obj)
        p_task_timing_end(MTR_LOGGER, strt)


    def DeleteCurrentMetrics(self, metric_type, entity_id):
        class_name = self.getClassfromMetricType(metric_type)
        try:
            DBSession.query(class_name).filter(class_name.entity_id==entity_id).filter(class_name.metric_type==metric_type).delete()
        except Exception, ex:
            LOGGER.error(to_str(ex))
            LOGGER.debug('Failed: DeleteCurrentMetrics')
            raise
