# yourapp/management/commands/seed_default_todos.py
from django.core.management.base import BaseCommand
from accounts.models import DefaultTodo, PersonalTodo

DEFAULTS = [
    {"name": "Subhi in Jama", "todo_type": "checkbox"},
    {"name": "Zhuhr in Jama", "todo_type": "checkbox"},
    {"name": "Asr in Jama", "todo_type": "checkbox"},
    {"name": "Maghrib in Jama", "todo_type": "checkbox"},
    {"name": "Tilawah", "todo_type": "number", "extra_field_label": "Page Number"},
    {"name": "Solatu Duah", "todo_type": "checkbox"},
    {"name": "Solatu Taobah", "todo_type": "checkbox"},
    {"name": "Qiyamul Layl", "todo_type": "number", "extra_field_label": "How many prayed"},
    {"name": "Witr", "todo_type": "checkbox"},
    {"name": "Adhkar", "todo_type": "checkbox"},
]

class Command(BaseCommand):
    help = "Seed default todos for sitting-member"

    def handle(self, *args, **kwargs):
        for i, item in enumerate(DEFAULTS):
            DefaultTodo.objects.get_or_create(
                name=item["name"],
                defaults={
                    "todo_type": item.get("todo_type", "checkbox"),
                    "extra_field_label": item.get("extra_field_label", ""),
                    "sort_order": i
                },
            )
        self.stdout.write(self.style.SUCCESS("Seeded default todos"))
