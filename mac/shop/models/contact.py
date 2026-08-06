from django.db import models



class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, default="")
    phone_number = models.CharField(max_length=20)
    desc = models.CharField(max_length = 400, default="")


    def __str__(self):
        return self.name
    