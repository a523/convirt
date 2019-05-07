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

function getDocumentDimensions() {
  var myWidth = 0, myHeight = 0;
  if( typeof( window.innerWidth ) == 'number' ) {
    //Non-IE
    myWidth = window.innerWidth;
    myHeight = window.innerHeight;
  } else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
    //IE 6+ in 'standards compliant mode'
    myWidth = document.documentElement.clientWidth;
    myHeight = document.documentElement.clientHeight;
  } else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
    //IE 4 compatible
    myWidth = document.body.clientWidth;
    myHeight = document.body.clientHeight;
  }
//  window.alert( 'Width = ' + myWidth );
//  window.alert( 'Height = ' + myHeight );
    if(document.all){//alert('IE');
        myHeight = myHeight-5;
    }
  var dims=new Array();
  dims.push(myWidth);
  dims.push(myHeight);
  return dims;
}

var centerPanel,leftnav_treePanel;
var tasks_grid;
function dashboardUI(){
    registration();
    update_ui_manager();
    var method_map=new Array();
    method_map[convirt.constants.DATA_CENTER]='data_center';
    method_map[convirt.constants.SERVER_POOL]='server_pool';
    method_map[convirt.constants.MANAGED_NODE]='server';
    method_map[convirt.constants.DOMAIN]='vm';
    method_map[convirt.constants.IMAGE_STORE]='image_store';
    method_map[convirt.constants.IMAGE_GROUP]='image_group';
    method_map[convirt.constants.IMAGE]='image';
    
    var dims=getDocumentDimensions();
    //alert(dims[0]+"---"+dims[1])
    var myWidth = dims[0], myHeight = dims[1];
    
    var lbl_header=new Ext.form.Label({
        html:'<div align="center"><font size=4 face="Verdana" ><b>ConVirt 2.1</b></font></div>',
        id:'lbl_header'
    });
    
    var lbl_user=new Ext.form.Label({
        html:'<div align="left"><font size=2 face="Verdana" ><b>' + _('User') + ': ' + user_name + '</b></font></div>',
        id:'lbl_user'
    });

    var links="<div align='right'>";
    if(is_admin =='True'){        
        links+="<img style='cursor:pointer' title='Administration' src='/icons/admin.png' onclick=javascript:showWindow('"+_('Administration')+"',705,470,adminconfig()); ></img>&nbsp;";
    }
    links+="<img style='cursor:pointer' title='Change Password' src='/icons/chpass.png' onclick=javascript:showWindow('"+_("Password")+"',400,200,changepass(user_name)); ></img>&nbsp;";
    links+="<img style='cursor:pointer' title='Tasks' src='/icons/tasks.png' onclick=javascript:showWindow('"+_('Tasks')+"',740,370,Tasks());></img>&nbsp;"+
        "<img style='cursor:pointer' title='Logout' onclick=javascript:window.location='/user_logout' src='/icons/logout.png'></img>"+
        "</div>";

    var lbl_links=new Ext.form.Label({
        html:links,
        id:'lbl_links'
    });
        
    var westPanel=new Ext.Panel({
        region:'west',
        width:180,
        height:'100%',
        autoScroll:true,
        split:true,
        layout:"fit",
        defaults: {
            autoScroll:true
        },
        minSize: 50,
        maxSize: 300,
        border:false,
        id:'westPanel',
        cls:'westPanel'
    });

    var V = new Ext.ux.plugin.VisibilityMode({ bubble : false }) ;
    centerPanel=new Ext.TabPanel({
        minTabWidth: 115,
        tabWidth:135,
        cls:'central-panel-baground',
        activeTab:0,
        border:false,
        id:'centerPanel'
        ,defaults: {
          plugins: V,
          hideMode : 'nosize'
        }
        ,listeners:{
            resize:function(){
                if(centerPanel.rendered){
                	
                    centerPanel.doLayout();
                }
            }
            ,tabchange:function(tabpanel,tab){//alert(tabpanel.isRemoving);
                if(tabpanel.isRemoving==true){
                    return;
                }
                var node=leftnav_treePanel.getSelectionModel().getSelectedNode();
                var nodetype=node.attributes.nodetype;
                var tabid=tab.getId();
                //vnc console tabs will have id=(console+nodeid)
                if(tabid.indexOf('console')!=0){
                    //alert(tabid+"===="+nodetype+"===="+node.attributes.id);
                    var method=method_map[nodetype]+"_"+tabid+"_page";//alert(method)
                    eval(method+"(tab,node.attributes.id,node)")
                }

            }
            ,remove:function(container,component){
            	if (Ext.isIE) {
            	component.rendered =true;
            	container.render(component);
            	}
            	
            }
            ,beforeremove :function(container,component){
            	if (Ext.isIE) {
            	component.rendered =false;
            	}
            }
           
           
           
          
        }

    });

    var label_entity=new Ext.form.Label({
        html:getHdrMsg('')
    });
    var menu_store = new Ext.data.JsonStore({
        url: '/get_context_menu_items?menu_combo=True',
        root: 'rows',
        fields: ['text', 'value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_( "Error"),store_response.msg);
                }
            }
    });
    var menu_combo=new Ext.form.ComboBox({
        triggerAction:'all',
        store: menu_store,
        emptyText :_("Select Action"),
        displayField:'text',
        valueField:'value',
        width: 200,
        editable:false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'menu_group',
        id:'menu_group',
        mode:'local',
        listeners:{
            select:function(combo){
                var menu=new Ext.menu.Item({
                    id:menu_combo.getValue(),
                    tooltip:menu_combo.getRawValue()
                });
                var node=leftnav_treePanel.getSelectionModel().getSelectedNode();

                if(node){
                    handleEvents(node,menu_combo.getValue(),menu);
                }
            }
        }
    });
        
//    var menu_btn=new Ext.Button({
//        tooltip:'Show Context Menu',
//        tooltipType : "title",
//        icon:'icons/settings.png',
//        cls:'x-btn-icon',
//        listeners: {
//            click: function(btn,e){
//                var node=leftnav_treePanel.getSelectionModel().getSelectedNode();
//                if(node)
//                    node.fireEvent('contextmenu',node,e);
//            }
//        }
//    });
    var northPanel=new Ext.Panel({
        region:'north',
        title: 'North Panel',
        collapsible:false,
        layout:'anchor',
        header:false,
        split:false,
        border:false,
        height: 22,
        id:'northPanel'
    });    
    northPanel.add(toolbarPanel());

   tasks_grid=TasksGrid();
   var southPanel=new Ext.Panel({
        region:'south',
        title: _('Tasks'),
        collapsible:true,        
        layout:'fit',
        header:true,
        split:true,
        border:false,
        defaults: {
            autoScroll:true
        },
        collapsed:false,
        height: 120,
        minSize: 75,
        maxSize: 350,
        id:'southPanel'
        ,tools:[{
            id:'refresh',
            //qtip: 'Refresh form Data',
            // hidden:true,
            handler: function(event, toolEl, panel){
                tasks_grid.getStore().load();                
            }
        }]
        ,plugins: new Ext.ux.collapsedPanelTitlePlugin()
    });
    southPanel.add(tasks_grid);
    var ad_index=0;
    var ad = [["VMware", "http://www.convirture.com/solutions_vmware.php"], ["Hyper-V", "http://www.convirture.com/solutions_hyperv.php"],["Amazon EC2", "http://www.convirture.com/solutions_aws.php"],["OpenStack", "http://www.convirture.com/solutions_openstack.php"]]
    // javascript:showWindow('"+_('Administration')+"',705,470,adminconfig());
     var header_html_link= "<div class='header-container'>";
	    header_html_link+= "  <div class='header-left'>";
	    header_html_link+= "  <img src='images/logo_convirt.gif' alt='ConVirt Logo'/>";
	    header_html_link+= "  </div>";

    	header_html_link+="<div class=header-co>";
    	header_html_link+= "<div class='header-right-bottom'>";
    	header_html_link+="<p>"+_(edition_string+' '+version)+"</p>";
    	header_html_link+="</div>";
        header_html_link+="</div>";
        header_html_link+= "    <div class='header-right'>";
        header_html_link+= "        <div class='header-right-left'>";
        header_html_link+= "           <p>"+_('User')+" : </p><p>"+user_firstname+"</p>";
        header_html_link+= "        </div>";
        header_html_link+= "         <wr id='header-warning' class='warning'>  <a id='header-warning-link' href='#'> <img id='header-warning-img' src='icons/warning.png' title='' style='display:none;' /> </a> </wr>";
        
        header_html_link+= "        <div class='header-right-right'>";
        /*
        header_html_link+= "            <ul class='admin-nav-menu'>";
        if (is_admin == 'True') {
             header_html_link+= "           <li class='admin'><a href='#' onclick=javascript:showWindow('"+_('Administration')+"',705,470,adminconfig());></a></li>";
        }
        header_html_link+= "                <li class='task'><a href='#' onclick=javascript:showWindow('"+_('Tasks')+"',740,370,Tasks());></a></li>";
        header_html_link+= "                <li class='password'><a href='#' onclick=javascript:showWindow('"+_('Password')+"',400,200,changepass(user_name));></a></li>";
        header_html_link+= "                <li class='logout'><a href='#' onclick=javascript:window.location='/user_logout'></a></li>";
        header_html_link+= "            </ul>";
        */
var r1 = Object(); r1["isNew"] = false; r1["name"] = "Documentation"; r1["url"] = "http://www.convirture.com/wiki/index.php?title=Main_Page";
var r2 = Object(); r2["name"] = "Forums"; r2["url"] = "http://www.convirture.com/forums/";
var r3 = Object(); r3["name"] = "Certified Configurations"; r3["url"] = "http://convirture.com/support_configurations.php";
var r4 = Object(); r4["name"] = "FAQ"; r4["url"] = "http://www.convirture.com/wiki/index.php?title=Convirt2_faq";
var r5 = Object(); r5["name"] = "How To's"; r5["url"] = "http://www.convirture.com/wiki/index.php?title=Convirt2_Tutorials";
var r6 = Object(); r6["name"] = "Registration"; r6["url"] = "http://www.convirture.com/register.php?did=$did";
var defResData = [ r1, r2, r3, r4, r5, r6 ];

    var ajaxReq = ajaxRequest("/dashboard/get_resources", 0, "GET");
    ajaxReq.request({
        success: function(xhr) {
            showResourcesMenu(xhr.responseText);
        }
    });

function showResourcesMenu(resStr) {
    var elm = document.getElementById('resourcemenu');
    if (!elm) {
        setTimeout(showResourcesMenu(resStr), 5000);
        return true;
    }
    var resData = [];
    try {
        var res = Ext.util.JSON.decode(resStr);
        resData = Ext.util.JSON.decode(res["info"]);
    } catch (e) {
        resData = defResData;
    }
    var menu_html = '';
    menu_html += '      <ul class="submenu">';
    var newRes = '';
    for (i = 0; i < resData.length; i++) {
        r = resData[i];
        var newCls = '';
        if (r['isNew'] == true) {
            newCls = ' <img src="../images/star.png">';
            newRes = newCls;
        }
        menu_html += '        <li><a target="_blank" href="' + r['url'].replace('$did', did) + '">' + r['name'] + newCls + '</a></li>';
    }
    menu_html += '      </ul>';
    menu_html = '      <a target="_blank" href="http://www.convirture.com/getconvirt.php">Resources' + newRes + '</a>' + menu_html;
    elm.innerHTML = menu_html;
}

var resData = defResData;
var newRes = '';
var menu_html = '';
header_html_link += '<nav>';
header_html_link += '  <ul id="mainmenu">';
header_html_link += '    <li id="resourcemenu">';
menu_html += '      <ul class="submenu">';
for (i = 0; i < resData.length; i++) {
    r = resData[i];
    var newCls = '';
    if (r['isNew'] == true) {
        newCls = ' <img src="../images/star.png">';
        newRes = newCls;
    }
    menu_html += '        <li><a target="_blank" href="' + r['url'].replace('$did', did) + '">' + r['name'] + newCls + '</a></li>';
}
menu_html += '      </ul>';
menu_html = '      <a target="_blank" href="http://www.convirture.com/getconvirt.php">Resources' + newRes + '</a>' + menu_html;
header_html_link += menu_html;
header_html_link += '    </li>';

header_html_link += "                <li><a target='_blank' href='http://www.convirture.com/feedback.php?did=" + did +"' target='_blank'>Feedback</a></li>";
if (is_admin == 'True') {
    header_html_link += "                <li><a href='#' onclick=javascript:showWindow('"+_('Administration')+"',705,470,adminconfig());>Admin</a></li>";
}
header_html_link += "                <li><a href='#' onclick=javascript:showWindow('"+_('Tasks')+"',740,370,Tasks());>Tasks</a></li>";
header_html_link += "                <li><a href='#' onclick=javascript:showWindow('"+_('Password')+"',400,200,changepass(user_name));>Change Password</a></li>";
header_html_link += "                <li><a href='#' onclick=javascript:window.location='/user_logout'>Logout</a></li>";
header_html_link += '        </ul>';
header_html_link += '</nav>';

        header_html_link+= "        </div>";

        header_html_link+="<div class='header-right-right' style ='text-align:right' ><a style='text-decoration:none;color: #004C8A;' target='_blank' href=";
        var rand_no = Math.ceil(100*Math.random());
        if (rand_no%2==0){
            header_html_link+=convirt.constants.upgrade_to_ee+">"+_('Upgrade to ConVirt Enterprise');
        }else{
            header_html_link+=convirt.constants.learn_about_ee+">"+_('Learn about ConVirt Enterprise');
        }
        header_html_link+="</a></div>";
        header_html_link+= "    </div>";
        header_html_link+= "</div>";

    var headerPanel=new Ext.Panel({
        height:63,
        border:false,
        width:"100%",
        id:'headerPanel',
        cls:'headerPanel',
        layout:'column',
        html: header_html_link
    });

    var label_action=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("Actions")+'</div>'
    });

    var titlePanel=new Ext.Panel({
        layout:'fit',
        region:'center',
        split:true,
        margins: '2 2 2 0',
        width:'100%',
        tbar:[label_entity,{xtype:'tbfill'},label_action,"&nbsp;&nbsp;",menu_combo]
    });
    titlePanel.add(centerPanel);

    var borderPanel = new Ext.Panel({
        width:"100%",
        height:myHeight-60,
        layout:'border',
        id:'borderPanel',
        items: [westPanel,titlePanel,southPanel]
        ,monitorResize:true         
    });
    var outerPanel = new Ext.Panel({
        //renderTo:'content',
//        width:myWidth-5,
        //height:myHeight-5,
        border:false,
        width:"100%",
        height:"100%",
        id:'outerPanel',
        items: [ headerPanel,borderPanel]
        ,monitorResize:true 
        ,listeners:{
            resize:function(){
                var dims=getDocumentDimensions();
                //alert(dims[0]+"---"+dims[1])
                var myWidth = dims[0], myHeight = dims[1];
                if(borderPanel.rendered){
                    borderPanel.setHeight(myHeight-30);
                    borderPanel.doLayout();
                }
            }
        }
    }); 
    
    var summaryPanel=new Ext.Panel({
        title   : _('Overview'),
        closable: false,
        //autoScroll:true,
        defaults: {
            autoScroll:true
        },
        layout:'fit',
        width:400,
        id:'summary'
        ,listeners:{
            activate:function(panel){
                if(panel.rendered){
                    panel.doLayout();
                }
            }
        } 
    }); 
    var infoPanel=new Ext.Panel({
        title   : _('Information'),
        closable: false,
        //layout  : 'anchor',
        id:'info',
        height:600,
        autoScroll:true,
        defaults: {
            autoScroll:true
        },
        layout:'fit',
        //frame:true,
        cls:'westPanel'
        ,listeners:{
            activate:function(panel){
                if(panel.rendered){
                    panel.doLayout();
                }
            }
        }
    });
    var configPanel=new Ext.Panel({
        title   : _('Configuration'),
        closable: false,
        layout  : 'fit',
        id:'config',
        autoScroll:true,
        defaults: {
            autoScroll:true
        }
        ,listeners:{
            activate:function(panel){
                if(panel.rendered){
                    panel.doLayout();
                }
            }
        }
    });
    var vminfoPanel=new Ext.Panel({
        title   : _('Virtual Machines'),
        closable: false,
        layout  : 'fit',
        id:'vminfo',
        autoScroll:true,
        defaults: {
            autoScroll:true
        }
        ,listeners:{
            activate:function(panel){
                if(panel.rendered){
                    panel.doLayout();
                }
            }
        }
    });

    leftnav_treePanel = new Ext.tree.TreePanel({
        rootVisible : false,
        useArrows: true,
        autoScroll: true,
        animate: true,
        enableDD: true,
        containerScroll: true,
        border: false,
        el: westPanel.getEl(),
        layout: 'fit',
        cls:'leftnav_treePanel',
        listeners: {
            beforenodedrop: function(e){
                processDrop(e);
                return false;
            }
            ,contextmenu: function(node, e) {
                if (node.attributes.nodetype == convirt.constants.SPECIAL_NODE){                 
                    
                    return;

                }
                showContextMenu(node, e);
            },beforeexpandnode:function(node){
                if(node.attributes.id!="0" && node.childNodes.length==1){//checking root node node.attributes.id!="0"
                        if(node.childNodes[0].attributes.id=="dummy_node"){
                            node.childNodes[0].getUI().hide();
                            node.fireEvent('click',node);

                        }
                 }
             }
        }
    });

    new Ext.tree.TreeSorter(leftnav_treePanel,{
        folderSort:true,
        dir:'ASC'
    });

    leftnav_treePanel.on('beforeclick',function(node,e){

        if (node.attributes.nodetype == convirt.constants.SPECIAL_NODE){
            Ext.MessageBox.alert(_("Message"),"Too many Servers in the server pool to show in the navigator.<br/>\
                                    Please use Servers tab to find the Server you are looking for.");
            return false;

        }
    });

    leftnav_treePanel.on('click',function(node,e){

        if(node.attributes.clickable==convirt.constants.OUTSIDE_DOMAIN){
            return;
        }

        var iconClass=node.getUI().getIconEl().className;
        node.getUI().getIconEl().className="x-tree-node-icon loading_icon";
        var ajaxReq = ajaxRequest(node.attributes.url,0,"GET",true);
        //checkToolbar(node);
        if(node.attributes.nodetype==convirt.constants.DOMAIN){
            menu_combo.reset();
            menu_store.load({
                params:{
                    node_id:node.attributes.id,
                    node_type:node.attributes.nodetype
                }
            });
            (function(){
                addTabs(centerPanel,[summaryPanel,configPanel]);
            }).defer(25);            

            //getVNCInfo(node.parentNode,node,centerPanel);
            //updateInfoTab(InfoGrid(node),true);
            node.getUI().getIconEl().className=iconClass;
            label_entity.setText(getHdrMsg(node.text),false);
            
            return;
        }else if(node.attributes.nodetype==convirt.constants.IMAGE){
            menu_combo.reset();
            menu_store.load({
                params:{
                    node_id:node.attributes.id,
                    node_type:node.attributes.nodetype
                }
            });
            (function(){
                addTabs(centerPanel,[summaryPanel,infoPanel,vminfoPanel]);
            }).defer(25);

            node.getUI().getIconEl().className=iconClass;
            label_entity.setText(getHdrMsg(node.text),false);
            
            infoPanel.setTitle(_('Description'));
            vminfoPanel.setTitle( _('Virtual Machines'));
            return;       
        }   

        //showChart(node.attributes.nodetype ,"CPU",node.attributes.id,"DDDD","DTD",null,null,"DDD");
        ajaxReq.request({
            success: function(xhr) {

                node.getUI().getIconEl().className=iconClass;
                //alert(xhr.responseText+"-------------"+xhr.responseXML);
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(!response.success){
                    if(node.attributes.nodetype==convirt.constants.MANAGED_NODE &&
                            response.msg==_('Server not authenticated.')){
                        showWindow(_("Credentials for ")+node.text,280,150,credentialsform(node));
                        return;
                    }
                    Ext.MessageBox.alert(_("Failure"),response.msg);
                    return;
                }  
                
                label_entity.setText(getHdrMsg(node.text),false);
                menu_combo.reset();
                menu_store.load({
                    params:{
                        node_id:node.attributes.id,
                        node_type:node.attributes.nodetype
                    }
                });
                
                if(node.attributes.nodetype==convirt.constants.MANAGED_NODE){
                    
                    addTabs(centerPanel,[summaryPanel,configPanel,vminfoPanel]);
                    vminfoPanel.setTitle( _('Virtual Machines'));                    
                }else if(node.attributes.nodetype==convirt.constants.IMAGE_STORE ){

                    addTabs(centerPanel,[summaryPanel]);
                }else if(node.attributes.nodetype==convirt.constants.IMAGE_GROUP){

                    addTabs(centerPanel,[summaryPanel]);
                }else if(node.attributes.nodetype==convirt.constants.SERVER_POOL){

                    addTabs(centerPanel,[summaryPanel,configPanel,vminfoPanel]);
                    vminfoPanel.setTitle(_('Servers'));
                }else if(node.attributes.nodetype==convirt.constants.DATA_CENTER) {
                    
                    addTabs(centerPanel,[summaryPanel,configPanel,vminfoPanel]);
                    vminfoPanel.setTitle(_('Servers'));
                }
                var r_children=response.nodes;
                var n_children=node.childNodes;
                var new_nodes=get_new_nodes(r_children,node);
                var del_nodes=get_del_nodes(r_children,n_children);
                //alert(node.attributes.text+"===dash==new=="+new_nodes+"del=="+del_nodes);
                if(new_nodes.length!=0)
                    appendChildNodes(new_nodes,node);
                if(del_nodes.length!=0)
                    removeNodes(node,del_nodes);
//                removeChildNodes(del_nodes);
//                appendChildNodes(response.nodes,node);
                node.expand();
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                node.getUI().getIconEl().className=iconClass;
            }
        });

    }); 

    // SET the root node.
    var rootNode = new Ext.tree.TreeNode({
        text		: 'Root Node',
        draggable: false,
        id		: '0'
    });

    var ajaxReq=ajaxRequest("get_nav_nodes",0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                appendChildNodes(response.nodes,rootNode);
                rootNode.expand();
                rootNode.firstChild.fireEvent('click',rootNode.firstChild);
                get_app_updates();
                }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
 
    westPanel.add(leftnav_treePanel);

    leftnav_treePanel.setRootNode(rootNode);
    //leftnav_treePanel.render();

    return outerPanel; 
}
function registration(){
    
    if(registered=='True'){
        return true;
    }
    var url="http://www.convirture.com/register.php?did="+did;
    window.open(url, "_blank");

    var url="/dashboard/set_registered";
    var ajaxReq=ajaxRequest(url,0,"GET");
    ajaxReq.request({
        success: function(xhr) {

        },
        failure: function(xhr){
            
        }

    })
    
    return true;
}

function appendGrid(summaryPanel,grid){ 
    if(summaryPanel.items)
        summaryPanel.removeAll(true);
    summaryPanel.add(grid);
    grid.render('summaryPanel');

    summaryPanel.doLayout();    
}

function updateInfoTab(child,keepActive){
    var actTab=centerPanel.getActiveTab();    
    var infopanel=centerPanel.getItem('infoPanel');
    centerPanel.setActiveTab(infopanel);
    if (infopanel!=null){
        infopanel.removeAll();
        infopanel.add(child);
        infopanel.doLayout();
        if(!keepActive)
            centerPanel.setActiveTab(actTab);
    }
}

function getSshWindow(node){
        var response  = null;
        var platform = '';
        if(Ext.isLinux){
        	platform = 'linux'
        }else if(Ext.isWindows){
        	platform = 'windows'
        }
        var url='get_ssh_info?node_id='+node.id+'&client_platform='+platform
        var ajaxReq = ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {//alert(xhr.responseText);
                response=Ext.util.JSON.decode(xhr.responseText);
                showWindow(_('SSH Terminal'),450,260,show_ssh_window(node,response));
//                if(response){ 
//                    response = response.vnc;
//                 }else{
//                    Ext.MessageBox.alert(_("Failure"),response.msg);
//                }
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
            }
        });
}

function getVNCInfo(node,dom){
    //    if(!Java0Installed){
    //        Ext.MessageBox.alert( _("Warning") , _("Your Browser does not support java applets.")+"<br>"+
    //                            _("Please install the Java Runtime Environment Plugin."));
    //        return;
    //    }
    var consolePanel=centerPanel.getItem('console'+dom.attributes.id);
    if (consolePanel != null ){
        centerPanel.remove(consolePanel);
    }
    //if (consolePanel == null ){
    var url='get_vnc_info?node_id='+node.attributes.id+'&dom_id='+dom.attributes.id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    if (dom.getUI().getIconEl()!=null){
        var iconClass=dom.getUI().getIconEl().className;
        dom.getUI().getIconEl().className="x-tree-node-icon loading_icon";
    }
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            if (dom.getUI().getIconEl()!=null){
                dom.getUI().getIconEl().className=iconClass;
            }
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){

                var host=response.vnc.hostname;
                var port=response.vnc.port;
                var height=response.vnc.height;
                var width=response.vnc.height;
                var new_window=response.vnc.new_window;
                var show_control=response.vnc.show_control;
                var encoding=response.vnc.encoding;
                var restricted_colours=response.vnc.restricted_colours;
                var offer_relogin=response.vnc.offer_relogin;

                if(port=='00'){
                    Ext.MessageBox.alert(_("Message"),_("Virtual Machine is not Running."))
                    return;
                }

                var applet='<applet code="VncViewer.class" archive="/jar/SVncViewer.jar"'+
                'width="'+width+'" height="'+height+'">'+
                '<param name="HOST" value="'+host+'">'+
                '<param name="PORT" value="'+port+'">'+
                '<param name="Open new window" value="'+new_window+'">'+
                '<param name="Show controls" value="'+show_control+'">'+
                '<param name="Encoding" value="'+encoding+'">'+
                '<param name="Restricted colors" value="'+restricted_colours+'">'+
                '<param name="Offer relogin" value="'+offer_relogin+'">'+
                '</applet>';
                //var msg=response.vnc.msg;
                create_applet_tab(dom,applet,response);
                
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            if (dom.getUI().getIconEl()!=null){
                dom.getUI().getIconEl().className=iconClass;
            }
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
//    }else{
//        centerPanel.setActiveTab(consolePanel);
//    }
}

function getCMDInfo(dom,cmd,response){

    var consolePanel=centerPanel.getItem('console'+dom.attributes.id);
    if (consolePanel != null ){
        centerPanel.remove(consolePanel);
    }

    if(response.vnc.port=='00'){
        Ext.MessageBox.alert(_("Message"),_("Virtual Machine is not Running."))
        return;
    }


    var applet='<applet code="AppletRunner.class" archive="/jar/SAppletRunner.jar"'+
    ' width="1" height="1">'+
    '<param name="command" value="'+cmd+'">'+
    '</applet>';
    create_applet_tab(dom,applet,response);            
}

function create_applet_tab(dom,applet,response){
    var myData = [
        ['VNC Host',response.vnc.hostname],
        ['VNC Port',response.vnc.port],
        ['VNC Forwarded Port',response.vnc.server+" : "+response.vnc.vnc_display],
        ['Log File',response.vnc.temp_file]
    ];

    var summary_vnc_store = new Ext.data.SimpleStore({
        fields: [
            {name: 'name'},
            {name: 'value'}
        ]
    });

    // manually load local data
    summary_vnc_store.loadData(myData);
    var warn_tip=_('<font size="1" face="verdana" >\n\
                        <b> Note :</b> Java applet should be enabled in the browser for VNC.</font>');

    var label_summary=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("VNC Display Information")+'&nbsp;&nbsp;</div>'
    });
    var summary_vnc_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        stripeRows: true,
        autoHeight:true,
        border:true,
        cls:'hideheader',
        width:'75%',
        height: 150,
        enableHdMenu:false,
        enableColumnMove:false,
        autoExpandColumn:1,
        autoScroll:true,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [
        {
            header: "",
            width: 200,
            sortable: false,
            css:'font-weight:bold; color:#414141;',
            dataIndex:'name'
        },{
            header: "",
            width: 220,
            sortable: false,
            dataIndex:'value'
        }
        ],
        store:summary_vnc_store,
        tbar:[label_summary]
    });

    consolePanel=new Ext.Panel({
        title   : dom.text+"&nbsp;&nbsp;&nbsp;",
        closable: true,
        layout  : 'fit',
        id      :'console'+dom.attributes.id,
        html    : "<br/>"+warn_tip+"<br/>"+applet,
        bodyStyle:'padding-top:10px;padding-left:10px;padding-right:10px',
        bodyBorder:false
        ,cls:'westPanel'
    });
    consolePanel.add(summary_vnc_grid)
    centerPanel.add(consolePanel);
    centerPanel.setActiveTab(consolePanel);
}

function addTabs(prntPanel,childpanels){
	
	
    if(prntPanel.items){
        prntPanel.isRemoving=true;
//       	prntPanel.removeAll(true);
        
        
        prntPanel.items.each(function(tab){
            //vnc console tabs will have id=(console+nodeid)
            if(tab.getId().indexOf('console')!=0){
             		prntPanel.remove(tab,true);
            }
        })
        
        
        
   }
    prntPanel.isRemoving=false;
    for(var i=0;i<childpanels.length;i++){
    	
        prntPanel.insert(i,childpanels[i]);
    }
    if(childpanels.length>0){
        prntPanel.setActiveTab(childpanels[0]);
    }
}


function getHdrMsg(node){
    return '<div class="toolbar_hdg" >'+node+'<div>';
}

var get_updated_entities_req_handler = new convirt.communication_failure_handler();
function update_ui_manager(){
    var time=page_refresh_interval*1000
    var update_task = {
        run : function() {
            var can_send_request = get_updated_entities_req_handler.can_send_request();
//            console.log("--get_updated_entities--can_send_request---"+can_send_request);
            if (can_send_request){
                    var url="/node/get_updated_entities?user_name="+user_name;
                    var ajaxReq = ajaxRequest(url,0,"GET",true);
                    get_updated_entities_req_handler.start(ajaxReq);
                    ajaxReq.request({
                        success: function(xhr) {
        //                    alert(xhr.responseText);
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            get_updated_entities_req_handler.end(response);
                            if(!response.success){
                                Ext.MessageBox.alert(_("Failure"),response.msg);
                                return;
                            }
        //                    alert(response.update_details.length);
                            var node_ids;
        //                    if(eval("response.update_details."+user_name)){
                            if(response.node_ids.length>0){
                                node_ids=response.node_ids;
                                var selected_node=leftnav_treePanel.getSelectionModel().getSelectedNode();
                                for(var i=0;i<=node_ids.length;i++){
                                    var node=leftnav_treePanel.getNodeById(node_ids[i]);
                                    if(node!=null){
        //                                if(node.isExpanded()){
                                            update_expanded_node(node);
        //                                }

                                        if(selected_node!=null && selected_node.attributes.id==node_ids[i]){
                                            //selected_node.fireEvent('click',selected_node);
                                            var tab=centerPanel.getActiveTab();
                                            //alert(tab.getId());
                                            centerPanel.fireEvent('tabchange',centerPanel,tab);
                                        }
                                    }
                                }
                            }
                        },
                        failure: function(xhr){
                             get_updated_entities_req_handler.set_warning(xhr.statusText);
                            //Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                        }
                    });

          }//can_send_request

        },
        interval :time
    };
    //var task_runner = new Ext.util.TaskRunner();
    task_runner.start(update_task);
}

function get_app_updates(){
    var url="/get_app_updates";
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(!response.success){
//                Ext.MessageBox.alert(_("Failure"),response.msg);
                return;
            }            
            var updates  = response.updates;            
            //alert(updates);
            var value= "";
            var description="",nbsp="&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
            var l = updates.length;
            for(var i=0;i<l;i++){
                var update= updates[i];
                description=update.description;
                description=description.replace( /<li>/g, nbsp);
                description=description.replace( /<\/li>/g, "<br/>");
//                alert("-----"+description);
                value +="<CENTER>"+"<b>"+update.title+"</CENTER>"+"</b>"+"<br/>"+"<br/>"+"<b>Published Date:</b>"
                    +update.pubDate+"<br />"+"<br />"+description+"<br/>"+"<br/><hr><br/>";
            }            
            if(l>0){
//                alert(value);
                var popup=new Ext.Window({
                    title : "Updates",
                    width : 500,
                    height: 400,
                    modal : true,
                    resizable : true,
                    minWidth :250,
                    minHeight :250,
                    autoScroll:true,
                    html    : value
                });     
                popup.show();
            }
        },
        failure: function(xhr){
//            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function show_ssh_window(node,response){
//    var vm_platform=response.vm_platform;
    if(!response.success){
        Ext.MessageBox.alert( _("Failure") , response.msg);
    }

    cmd  = Ext.util.Format.trim(response.vnc.command);
    var applet='<applet code="AppletRunner.class" archive="/jar/SAppletRunner.jar"'+
    ' width="1" height="1">'+
    '<param name="command" value="'+cmd+'">'+
    '</applet>';

    var consolePanel=centerPanel.getItem('console'+node.id);
    if (consolePanel != null ){
        centerPanel.remove(consolePanel);
    }
    var help= ''
    var heading='SSH Connection Information';

    var label_summary=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_(heading)+'</div>'
    });

    var warn_tip=_('<font size="1" face="verdana" >\n\
                        <b> Note :</b> Java applet should be enabled in the browser for SSH.</font>');

    var ssh_data = [
                ['SSH Forwarding', response.vnc.forwarding]
            ];
    if (response.vnc.forwarding == 'Enabled'){
            ssh_data.push(['SSH Host', response.vnc.hostname]);
            ssh_data.push(['SSH Port', response.vnc.port]);
        }
    ssh_data.push(['Server', response.vnc.server]);

    var console_grid = get_console_grid(ssh_data, label_summary);

//    var consolePanel_heading=new Ext.Panel({
//        autoHeight:true,
//        border:true,
//        cls:'hideheader',
//        width:'75%',
//        height: 150,
//        frame:false,
//        tbar:[label_summary]
//    });

    consolePanel=new Ext.Panel({
        title   : node.text+"&nbsp;&nbsp;&nbsp;",
        closable: true,
        layout  : 'fit',
        id      :'console'+node.id,
        html    : "<br/>"+warn_tip+"<br/>"+applet,
        bodyStyle:'padding-top:10px;padding-left:10px;padding-right:10px',
        bodyBorder:false
        ,cls:'westPanel'
    });

//    consolePanel.add(consolePanel_heading);
    consolePanel.add(console_grid);
    centerPanel.add(consolePanel);
    centerPanel.setActiveTab(consolePanel);
    return ' ';
}



function get_console_grid(data, label_summary)
{
    var summary_store = new Ext.data.SimpleStore({
        fields: [
            {name: 'name'},
            {name: 'value'}
        ]
    });
    
    summary_store.loadData(data);

    var summary_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        stripeRows: true,
        autoHeight:true,
        border:true,
        cls:'hideheader',
        width:'75%',
        height: 150,
        enableHdMenu:false,
        enableColumnMove:false,
        autoExpandColumn:1,
        autoScroll:true,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [
        {
            header: "",
            width: 200,
            sortable: false,
            css:'font-weight:bold; color:#414141;',
            dataIndex:'name'
        },{
            header: "",
            width: 220,
            sortable: false,
            dataIndex:'value'
        }
        ],
        store:summary_store,
        tbar:[label_summary]
    });

   return summary_grid
}



/*function show_log(file){

    var url="/node/get_vnc_log_content?file="+file;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    Ext.MessageBox.show({
        title:_('Please wait...'),
        msg: _('Please wait...'),
        width:300,
        wait:true,
        waitConfig: {
            interval:200
        }
    });
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                Ext.MessageBox.hide();
                showWindow(_("View Console log:")+" "+file,444,480,view_content(response.content));
            }
        },
        failure: function(xhr){
            Ext.MessageBox.hide();
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function view_content(content){

     var klbl=new Ext.form.Label({
         html: _(content)
     });

    var content_panel1=new Ext.Panel({
        closable: true,
        height:'100%',
        border:false,
        width:'100%',
        labelAlign:'left',
        layout:'form',
        frame:true,
        autoScroll:true,
        labelSeparator:' ',
        id:"content_panel1",
        items: [klbl]
    });

      var content_panel2=new Ext.Panel({
        height:450,
        border:true,
        width:'100%',
        labelAlign:'left',
        layout:'form',
        autoScroll:true,
        labelSeparator:' ',
        id:"content_panel2",
        items:[content_panel1],
        bbar:[{xtype: 'tbfill'},
                new Ext.Button({
                name: 'close',
                id: 'close',
                text:_('Close'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        closeWindow();
                    }
                }
            })

    ]
    });

    return content_panel2;


}*/
