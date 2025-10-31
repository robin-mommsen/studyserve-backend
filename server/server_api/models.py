import re
from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.primitives.serialization import load_ssh_public_key
from django.db import models
from config import settings
from project_api.models import Project
from core.models import TimeStampedModel
from server_config_api.models import ServerConfig
from django.core.exceptions import ValidationError
import jsonschema

def validate_ssh_keys(value):
    schema = {
        "type": "object",
        "properties": {
            "keys": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["keys"]
    }
    try:
        jsonschema.validate(instance=value, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        raise ValidationError(f"Invalid ssh_keys: {e.message}")

    for key in value.get("keys", []):
        try:
            public_key = load_ssh_public_key(key.encode())
            if not isinstance(public_key, (rsa.RSAPublicKey, ed25519.Ed25519PublicKey)):
                raise ValidationError(f"Unsupported SSH key type: {key}")
        except (ValueError, InvalidKey, Exception) as e:
            raise ValidationError(f"Invalid SSH key format: {key}. Error: {str(e)}")

def normalize_hostname(value: str) -> str:
    if not value:
        return value
    value = value.lower().strip()
    value = value.replace(" ", "-")
    value = re.sub(r'[^a-z0-9-]', '', value)
    value = re.sub(r'-+', '-', value)
    value = value.strip('-')
    return value[:63]


class Server(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hostname = models.CharField(max_length=63)
    server_config = models.ForeignKey(ServerConfig, on_delete=models.SET_NULL, null=True)
    expiry_timestamp = models.IntegerField(null=True, blank=True)
    ssh_keys = models.JSONField(validators=[validate_ssh_keys])
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, blank=True, default='creating')
    vps_status = models.CharField(max_length=20, null=True, blank=True, default='offline')
    unlimited = models.BooleanField(default=False, blank=True)
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    world_id = models.CharField(max_length=10, null=True, blank=True)
    in_progress = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'servers'

    def save(self, *args, **kwargs):
        self.hostname = normalize_hostname(self.hostname)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.hostname

class AnsibleScript(TimeStampedModel):
    description = models.CharField(max_length=255)
    script = models.TextField()

    class Meta:
        db_table = 'ansible_scripts'

    def __str__(self):
        return self.description