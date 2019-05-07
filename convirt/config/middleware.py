# -*- coding: utf-8 -*-
"""WSGI middleware initialization for the convirt application."""

from convirt.config.app_cfg import base_config
from convirt.config.environment import load_environment

from convirt.core.utils.utils import setup_deployment,update_vm_status, storage_stats_data_upgrade, \
        unreserve_disks_on_cms_start, add_deployment_stats_task
from convirt.core.services.core import ServiceCentral
from convirt.model.Metrics import MetricsService
from convirt.model import zopelessmaker
from convirt.viewModel import Basic
from convirt.core.utils.NodeProxy import Node
import tg,os

import atexit

__all__ = ['make_app']

# Use base_config to setup the necessary PasteDeploy application factory. 
# make_base_app will wrap the TG2 app with all the middleware it needs. 
make_base_app = base_config.setup_tg_wsgi_app(load_environment)


def make_app(global_conf, full_stack=True, **app_conf):
    """
    Set convirt up with the settings found in the PasteDeploy configuration
    file used.
    
    :param global_conf: The global settings for convirt (those
        defined under the ``[DEFAULT]`` section).
    :type global_conf: dict
    :param full_stack: Should the whole TG2 stack be set up?
    :type full_stack: str or bool
    :return: The convirt application with all the relevant middleware
        loaded.
    
    This is the PasteDeploy factory for the convirt application.
    
    ``app_conf`` contains all the application-specific settings (those defined
    under ``[app:main]``.
    
   
    """
    app = make_base_app(global_conf, full_stack=True, **app_conf)

    setup_deployment()
    update_vm_status()
    try:
        Basic.getImageStore().init_scan_dirs()
    except Exception, e:
        print "Error while scanning the image store ", e
    try:
        storage_stats_data_upgrade()
    except Exception, e:
        print "Error while recomputing storage stats ", e
    try:
        unreserve_disks_on_cms_start()
    except Exception, e:
        print "Error while unreserving storage disks ", e

    #start the services thread
    #maker should already have been configured by calling init_model
    sc = ServiceCentral(zopelessmaker)
    sc.start()
    atexit.register(sc.quit)
    base_config.convirt_service_central = sc
    MetricsService().init_mappers()
    Node.use_bash_timeout=eval(tg.config.get("use_bash_timeout"))
    Node.default_bash_timeout=tg.config.get("bash_default_timeout")
    Node.bash_dir=os.path.join(tg.config.get('convirt_cache_dir'),'common/scripts')
    Node.local_bash_dir=tg.config.get("common_script")
    # Wrap your base TurboGears 2 application with custom middleware here
    try:
        add_deployment_stats_task()
    except Exception, e:
        print "Error while adding deployment stats task", e
    return app
