# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Task'
        db.delete_table('contribute_task')


    def backwards(self, orm):
        
        # Adding model 'Task'
        db.create_table('contribute_task', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('view', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.View'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('contribute', ['Task'])


    models = {
        
    }

    complete_apps = ['contribute']
