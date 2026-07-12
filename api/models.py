from django.db import models
from django.core.exceptions import ValidationError

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)

    def clean(self):
        super().clean()
        if not self.username or not self.username.strip():
            raise ValidationError("Username cannot be empty.")
        if not self.password_hash or not self.password_hash.strip():
            raise ValidationError("Password hash cannot be empty.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Conversation(models.Model):
    part_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_part_1', db_column='Part_1_id')
    part_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_part_2', db_column='Part_2_id')
    last_update = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.part_1_id and self.part_2_id:
            if self.part_1_id == self.part_2_id:
                raise ValidationError("Participants must be different users.")
            
            exists = Conversation.objects.filter(
                models.Q(part_1=self.part_1, part_2=self.part_2) |
                models.Q(part_1=self.part_2, part_2=self.part_1)
            ).exclude(pk=self.pk).exists()
            if exists:
                raise ValidationError("A conversation between these two users already exists.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Conversation {self.id}: {self.part_1.username} & {self.part_2.username}"


class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('games', 'Games'),
    ]
    conv = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', db_column='conv_id')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', db_column='sender_id')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    client_tx_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.conv_id and self.sender_id:
            if self.sender_id != self.conv.part_1_id and self.sender_id != self.conv.part_2_id:
                raise ValidationError("The sender must be a participant in the conversation.")
        if not self.content or not self.content.strip():
            raise ValidationError("Message content cannot be empty.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message {self.id} from {self.sender.username} in Conv {self.conv_id}"


class Games(models.Model):
    title = models.CharField(max_length=255)
    desc = models.TextField()
    url = models.URLField()

    def clean(self):
        super().clean()
        if not self.title or not self.title.strip():
            raise ValidationError("Game title cannot be empty.")
        if not self.desc or not self.desc.strip():
            raise ValidationError("Game description cannot be empty.")
        if not self.url or not self.url.strip():
            raise ValidationError("Game url cannot be empty.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
