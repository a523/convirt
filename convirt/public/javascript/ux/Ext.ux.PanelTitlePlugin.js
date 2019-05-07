/*
*   ConVirt   -  Copyright (c) 2008 Convirture Corp.
*   ======

* ConVirt is a Virtualization management tool with a graphical user
* interface that allows for performing the standard set of VM operations
* (start, stop, pause, kill, shutdown, reboot, snapshot, etc...). It
* also attempts to simplify various aspects of VM lifecycle management.


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Jd <jd_jedi@users.sourceforge.net>
*/
Ext.ux.collapsedPanelTitlePlugin = function ()
{
    this.init = function(p) {
        if (p.collapsible)
        {
            var r = p.region;
            if ((r == 'north') || (r == 'south'))
            {
                p.on ('render', function()
                    {
                        var ct = p.ownerCt;
                        ct.on ('afterlayout', function()
                            {
                                if (ct.layout[r].collapsedEl)
                                {
                                    p.collapsedTitleEl = ct.layout[r].collapsedEl.createChild ({
                                        tag: 'span',
                                        cls: 'x-panel-collapsed-text',
                                        html: "<div style='font-size:11px'>&nbsp;"+p.title+"</div>"
                                    });
                                    p.setTitle = Ext.Panel.prototype.setTitle.createSequence (function(t)
                                        {p.collapsedTitleEl.dom.innerHTML = t;});
                                }
                            }, false, {single:true});
                        p.on ('collapse', function()
                            {
                                if (ct.layout[r].collapsedEl && !p.collapsedTitleEl)
                                {
                                    p.collapsedTitleEl = ct.layout[r].collapsedEl.createChild ({
                                        tag: 'span',
                                        cls: 'x-panel-collapsed-text',
                                        html: "<div style='font-size:11px'>&nbsp;"+p.title+"</div>"
                                    });
                                    p.setTitle = Ext.Panel.prototype.setTitle.createSequence (function(t)
                                        {p.collapsedTitleEl.dom.innerHTML = t;});
                                }
                            }, false, {single:true});
                    });
            }
        }
    };
}