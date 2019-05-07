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

function loadXMLDoc(response,isFile)
{
    try //Internet Explorer
    {
        xmlDoc=new ActiveXObject("Microsoft.XMLDOM");
        xmlDoc.async=false;
        xmlDoc.loadXML(response);
        return xmlDoc;
    }
    catch(e)
    {
        try //Firefox, Mozilla, Opera, etc.
        {
            parser=new DOMParser();
            xmlDoc=parser.parseFromString(response,"text/xml");
            return xmlDoc;
        }
        catch(e) {
            alert("Your Browser is not capable of XML Dom parsing. "+e.message)
        }
    }
}
