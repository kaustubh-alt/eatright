from django.db import models
import uuid
from datetime import date
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import IntegrityError



CATEGORY_CHOICES = [
        (1, 'Male'),
        (2, 'Female'),
        (3, 'Non-Binary'),
    ]

# Create your models here.
class userdb(models.Model):
    userid = models.CharField(max_length=12, unique=True, editable=False)
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    gender = models.IntegerField(choices=CATEGORY_CHOICES, default=1)
    dob = models.DateField()
    age = models.IntegerField(default=20)

    
    def save(self, *args, **kwargs):
        if not self.userid:
            self.userid = self.generate_unique_userid()
        if self.dob:
            self.age = self.calculate_age()

        super().save(*args, **kwargs)# type: ignore

    def calculate_age(self):
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))


    def generate_unique_userid(self):
        # Generate a UUID and truncate it to 8 characters, then add a prefix
        while True:
            new_id = 'USR' + str(uuid.uuid4())[:8].upper()
            if not userdb.objects.filter(userid=new_id).exists():
                return new_id

    USERNAME_FIELD = 'user'
    REQUIRED_FIELDS = ['email', 'dob', 'gender']

class userfavoritedishes(models.Model):
    id = models.AutoField
    userid = models.ForeignKey(userdb , on_delete=models.CASCADE)
    dishname = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['userid', 'dishname'], name='unique_fav_dish')
        ]
    
    def save(self, *args, **kwargs):
        try:
            # Attempt to save the record
            super().save(*args, **kwargs)
        except IntegrityError:
            # If there is an IntegrityError (e.g., unique constraint violation), silently handle it
            pass

class useraction(models.Model):
    actionid = models.AutoField
    userid = models.ForeignKey(userdb , on_delete=models.CASCADE)
    dishname = models.CharField(max_length=100)
    action = models.CharField(max_length=10)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['userid', 'dishname'], name='unique_user_dish')
        ]

    def save(self, *args, **kwargs):

       
        existing_record = useraction.objects.filter(userid=self.userid, dishname=self.dishname).first()

        if existing_record:
            
            if self.action is not existing_record.action:
                useraction.objects.filter(userid=self.userid, dishname=self.dishname).update(action=self.action, time=timezone.now())
                print(existing_record.userid,existing_record.time)    
        else:
            super().save(*args, **kwargs)



class userchat(models.Model):
    id = models.AutoField
    userid = models.ForeignKey(userdb , on_delete=models.CASCADE)
    user = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    userimage = models.URLField(max_length=200, null=True, blank=True)
    genimage = models.URLField(max_length=200, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)


