# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('fahrtenliste_main', '0005_tabellennamen'),
    ]

    operations = [
        migrations.RunSQL("insert into einstellung (name, wert_char) values ('name', '');", reverse_sql=""),
        migrations.RunSQL("insert into einstellung (name, wert_decimal) values ('kilometerpauschale', 0.3);",
                          reverse_sql=""),
    ]
