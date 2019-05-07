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

from convirt.model import *
from convirt.model.DBHelper import DBHelper
from convirt.core.utils.utils import to_unicode,to_str
from convirt.model.GenericCache import GenericCache
class AuthorizationService:
    def __init__(self,user=None):
        self.user=user        
        
    ##To check if the user has the privilege/permission to
    ##execute this operation on th entity
    def has_privilege(self,opname,entity=None):        
        return True

    def is_admin(self):
        u=self.user
        g=Group.by_group_name(to_unicode('adminGroup'))       
        return u.has_group(g)

    def get_ops(self,entity,op=None):#       
        filters=[Entity.entity_id==entity.entity_id]
        if op is not None:
            filters.append(Operation.id==op.id)
        ops=DBHelper().filterby(Operation,[Operation.entityType,Operation.opsGroup,Entity],
            filters,[Operation.display_seq])

        return ops

    def get_entities(self,entityType,parent=None):
        ents=[]
        type=DBHelper().find_by_name(EntityType,entityType)
        filters=[Entity.type_id==type.id]        
        
        if parent is not None:
            ids=[x.entity_id for x in parent.children]
            filters.append(Entity.entity_id.in_(ids))
        orderby=[Entity.name.asc()]
        ents=DBHelper().filterby(Entity,[],filters,orderby)
        return ents

    def get_entity_names(self,entityType,parent=None):
        ents=[]
        if entityType is None or parent is None:
            return []
        type=DBHelper().find_by_name(EntityType,entityType)        
        filters=[Entity.type_id==type.id]
        ids=[x.entity_id for x in parent.children]
        filters.append(Entity.entity_id.in_(ids))        
        
        ents=DBHelper().filterby(Entity,[],filters)
        ent_names=[]
        for ent in ents:
            ent_names.append(ent.name)
        return ent_names

    def get_entity_ids(self,entityType,parent=None):
        type=DBHelper().find_by_name(EntityType,entityType)
        filters=[Entity.type_id==type.id]
        if parent is not None:
            ids=[x.entity_id for x in parent.children]
            filters.append(Entity.entity_id.in_(ids))
        ents=DBHelper().filterby(Entity,[],filters)
        ent_ids=[]
        for ent in ents:
            ent_ids.append(ent.entity_id)
        return ent_ids

    def get_entity(self,entityId,entityType=None,parent=None):
        filters=[Entity.entity_id==entityId]
        
        if entityType is not None:
            type=DBHelper().find_by_name(EntityType,entityType)
            filters.append(Entity.type_id==type.id)
        if parent is not None:
            ids=[x.entity_id for x in parent.children]
            filters.append(Entity.entity_id.in_(ids))
        ents=DBHelper().filterby(Entity,[],filters)
        ent=None
        if(len(ents)>0):
            ent=ents[0]
        return ent

    def get_entity_by_name(self,name,entityType=None,parent=None):
        
        filters=[Entity.name==name]
        if entityType is not None:
            type=DBHelper().find_by_name(EntityType,entityType)
            filters.append(Entity.type_id==type.id)
        if parent is not None:
            ids=[x.entity_id for x in parent.children]
            filters.append(Entity.entity_id.in_(ids))
        ents=DBHelper().filterby(Entity,[],filters)
        ent=None
        if(len(ents)>0):
            ent=ents[0]
        return ent
    
    def get_all_entities(self):
        ents=DBHelper().filterby(Entity)

        return ents

    def add_entity(self,name,entity_id,entityType,parent):
        try:
            type=DBHelper().find_by_name(EntityType,entityType)
            e=Entity()
            e.name=name
            e.type=type
            e.entity_id=entity_id
            #e.parent=parent
            DBHelper().add(e)
            DBHelper().add(EntityRelation(parent.entity_id,entity_id,u'Children'))
            ###Added to remove the referential integrity error due to transaction
            ###that SA/MySQL innodb is supposed to take care
            gc=GenericCache()
            gc.on_add_entity(e.type.name)
            DBSession.flush()
        except Exception, e:
            raise e

        return e

    def remove_entity_by_id(self,entityId,entityType=None,parent=None):
        try:
            entity=self.get_entity(entityId, entityType,parent)
            self.delete_relations(entity)
            gc=GenericCache()
            gc.on_delete_entity(entityId, entity.type.name)
            DBHelper().delete(entity)
        except Exception, e:
            raise e

    def remove_entity(self,entity):
        try:
            self.delete_relations(entity)
            gc=GenericCache()
            gc.on_delete_entity(entity.entity_id, entity.type.name)
            DBHelper().delete(entity)
        except Exception, e:
            raise e

    def update_entity_by_id(self,entityId,name=None,parent=None,new_entityId=None):
        try:
            entity=self.get_entity(entityId)
            self.update_entity(entity,name=name,parent=parent,new_entityId=new_entityId)
            gc=GenericCache()
            gc.on_add_entity(entity.type.name)
        except Exception, e:
            raise e
    def update_entity(self,entity,name=None,parent=None,new_entityId=None):
        try:
            if name is not None:
                entity.name=name
            if parent is not None:
                old_prnt=entity.parents[0]                
                self.delete_entity_relation(old_prnt.entity_id,entity.entity_id,u'Children')
                DBHelper().add(EntityRelation(parent.entity_id,entity.entity_id,u'Children'))
            if new_entityId is not None:
                entity.entity_id=new_entityId
            DBHelper().add(entity)
            
        except Exception, e:
            raise e

    def get_entity_relation(self,src,dest,reln):
        er=DBHelper().filterby(EntityRelation,[],[EntityRelation.src_id==src,\
            EntityRelation.dest_id==dest,EntityRelation.relation==reln])
        return er

    def delete_entity_relation(self,src,dest,reln):
        DBHelper().delete_all(EntityRelation,[],[EntityRelation.src_id==src,\
            EntityRelation.dest_id==dest,EntityRelation.relation==reln])

    def delete_relations(self,entity):
        DBHelper().delete_all(EntityRelation,[],\
            [EntityRelation.src_id==entity.entity_id,
            EntityRelation.relation==u'Children'])
        DBHelper().delete_all(EntityRelation,[],\
            [EntityRelation.dest_id==entity.entity_id,
            EntityRelation.relation==u'Children'])
