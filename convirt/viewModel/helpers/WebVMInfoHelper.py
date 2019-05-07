from convirt.core.utils.utils import to_unicode,to_str
class WebVMInfoHelper:
    def __init__(self):
        #print "in WebVMInfoHelper-----------------"
        pass

    def append_info(self, vm,  name, param,typ,id):
        """ get the value of param from vm and append Name/Value in the
        tree at 'iter' position."""

        
        if not vm:
            return {}
        value = vm[param]
        if value:
            if type(value) == int:
                value = to_str(value)
            return dict(id=typ+to_str(id),label=name,value=value,type=typ,extra='')

        else:
            config = vm.get_config()
            if config:
                value = config[param]
                if value:
                    if type(value) == int:
                        value = to_str(value)
                    return dict(id=typ+to_str(id),label=name,value=value,type=typ,extra='')

            return dict(id=typ+to_str(id),label=name,value="N/A",type=typ,extra='')

    def get_categories(self):
        return [("GEN", "General"), ("BOOT", "Boot"), ("RESOURCE", "Resource")]

    def get_category_keys(self):
        return { "GEN" : [("name", "Name"), ("filename", "Filename") ],
                 "BOOT" : [("on_crash", "On Crash"),
                           ("on_reboot", "On Reboot")],
                 "RESOURCE" : [ ("memory", "Memory"),
                                ("vcpus", "CPU"),
                                ("vif", "Network"),
                                ("disk", "Disks") ]
                 }


    def get_vm_info(self, vm):

        result=[]
        cat_keys = self.get_category_keys()
        for (cat,cat_label) in self.get_categories():
            i=0
            for k, k_label in cat_keys[cat]:
                result.append(self.append_info( vm, k_label,k,cat_label,i))
                i+=1

        return result
