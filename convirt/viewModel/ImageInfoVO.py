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

# ImageInfoVO.py

class ImageInfoVO:
    def __init__(self, image):
        self.image = image

    def toXml(self, xml):
        image_info_xml = xml.createElement("ImageInfo")
        image_info_xml.setAttribute("name",     self.image.get_name())
        image_info_xml.setAttribute("id",       self.image.get_id())
        image_info_xml.setAttribute("platform", self.image.get_platform())
        image_info_xml.setAttribute("location", self.image.get_location())

        return image_info_xml

class ImageGroupInfoVO:
    def __init__(self, image_group):
        self.image_group = image_group

    def toXml(self, xml):
        image_group_xml = xml.createElement("ImageInfo")
        image_group_xml.setAttribute("name",self.image_group.get_name())
        image_group_xml.setAttribute("id",self.image_group.get_id())
        return image_group_xml

