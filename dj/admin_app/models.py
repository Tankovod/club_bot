# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AlembicVersion(models.Model):
    version_num = models.CharField(primary_key=True, max_length=32)

    class Meta:
        managed = False
        db_table = 'alembic_version'


class Club(models.Model):
    name = models.CharField(unique=True, max_length=64)
    tag = models.CharField(unique=True, max_length=16)
    photo = models.CharField(max_length=512, blank=True, null=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'club'


class Role(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=16)

    class Meta:
        managed = False
        db_table = 'role'


class UserClub(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, to_field='tg_id')
    club = models.ForeignKey(Club, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_club'


class Users(models.Model):
    tg_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=64, blank=True, null=True)
    first_name = models.CharField(max_length=128, blank=True, null=True)
    last_name = models.CharField(max_length=128, blank=True, null=True)
    phone = models.CharField(unique=True, max_length=16, blank=True, null=True)
    role = models.ForeignKey(Role, models.DO_NOTHING)
    date_sign_up = models.DateTimeField()
    is_male = models.BooleanField(blank=True, null=True)
    note = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = 'users'
