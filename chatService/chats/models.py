from django.db import models
import random
import os
import subprocess


def get_docker_container_ip():
    ip = subprocess.check_output(['hostname', '-I']).decode('utf-8').strip()
    return ip

def generate_identifier():
    return ''.join(random.choices('0123456789abcdef', k=8))

class Chat(models.Model):
    customer_id = models.IntegerField(blank=False)
    employee_id = models.IntegerField(blank=False)

    identifier = models.CharField(max_length=8, unique=True, default=generate_identifier)
    connect_url = models.CharField(max_length=128, blank=True)

    def save(self, *args, **kwargs):
        service_ip = get_docker_container_ip()
        service_port = os.getenv('PORT')

        self.connect_url = f"ws://localhost:{service_port}/chat/{self.identifier}"

        super(Chat, self).save(*args, **kwargs)
