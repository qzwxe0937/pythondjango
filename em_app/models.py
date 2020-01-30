from django.db import models

from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

# Create your models here.


class emStation(models.Model):
    update_time = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50, unique=True)
    enName = models.CharField(max_length=2, unique=True)
    orderNum = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        verbose_name_plural = '站別'
        verbose_name = '站別'

    def __str__(self):
        return '%s - %s' % (self.orderNum, self.name)

    def save(self, *args, **kwargs):
        self.enName = self.enName.lower()
        return super(emStation, self).save(*args, **kwargs)


class emCheckItem(models.Model):
    update_time = models.DateTimeField(auto_now_add=True)
    station = models.ForeignKey(
        emStation, on_delete=models.CASCADE, related_name='checkItems')
    checkID = models.CharField(max_length=10, unique=True)
    explain = models.CharField(max_length=200)
    size = models.CharField(max_length=1, default="L")
    cycleTime = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name_plural = '檢查項目'
        verbose_name = '檢查項目'

    def __str__(self):
        return '%s - %s' % (self.checkID, self.explain)


class emLine(models.Model):
    update_time = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=5, unique=True)
    station = models.ManyToManyField(emStation)
    lineOwner = models.CharField(max_length=10, blank=True, null=True)


    class Meta:
        verbose_name_plural = '線別'
        verbose_name = '線別'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        return super(emLine, self).save(*args, **kwargs)


class emCheckRecord(models.Model):
    update_time = models.DateTimeField(auto_now_add=True)

    ipAddr = models.GenericIPAddressField()
    giUser = models.CharField(max_length=20)

    checkLine = models.CharField(max_length=5)
    checkStation = models.CharField(max_length=50)
    checkItems = models.TextField()

    checkOwner = models.CharField(max_length=20)
    checkDate = models.DateField()
    checkFileName = models.CharField(max_length=200)
    checkFile = models.FileField(upload_to='em_app/%Y/%m/')

    def __str__(self):
        return '%s - %s - %s' % (self.id, self.checkDate, self.checkOwner)

    def checkItemList(self):
        return self.checkItems.split('\n')


class emFatpDetail(models.Model):
    update_time = models.DateTimeField(auto_now_add=True)

    line = models.ForeignKey(emLine, on_delete=models.CASCADE)
    station = models.ForeignKey(emStation, on_delete=models.CASCADE)
    checkID = models.ForeignKey(emCheckItem, on_delete=models.CASCADE)
    lastRecordID = models.ForeignKey(
        emCheckRecord, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return '%s - %s - %s - %s' % (self.line, self.station, self.checkID, self.lastRecordID)


class emSchedule(models.Model):
    update_time = models.DateTimeField(auto_now_add=True)
    line = models.CharField(max_length=5)
    day = models.DateField()
    periods = models.TextField()

    def __str__(self):
        return '%s - %s' % (self.line, self.day)
    

@receiver(m2m_changed, sender=emLine.station.through)
def emLineEdit(sender, instance, action, **kwargs):
    if action == 'post_add':
        for _station in instance.station.all():
            for _checkItem in _station.checkItems.all():
                emFatpDetail.objects.get_or_create(
                    line=instance,
                    station=_station,
                    checkID=_checkItem,
                )
    elif action == 'post_remove':
        keep_station = list(instance.station.all())
        for _row in emFatpDetail.objects.filter(line=instance):
            if _row.station not in keep_station:
                _row.delete()


@receiver(post_save, sender=emCheckItem)
def emCheckItemEdit(sender, instance, **kwargs):
    for _line in emLine.objects.all():
        if instance.station in _line.station.all():
            emFatpDetail.objects.get_or_create(
                line=_line,
                station=instance.station,
                checkID=instance,
            )


# @receiver(post_save, sender=emCheckRecord)
# def emAddCheckRecord(sender, instance, **kwargs):
#    print(sender, instance)
#    pass


# @receiver(m2m_changed, sender=emCheckRecord.checkItem.through)
# def emAddCheckRecord(sender, instance, action, **kwargs):
#    if action == 'post_add':
#        for _checkItem in instance.checkItem.all():
#            emFatpDetail.objects.filter(
#                line=instance.checkLine,
#                checkID=_checkItem,
#            ).update(
#                lastRecordID=instance,
#            )
