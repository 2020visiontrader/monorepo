"""
Add brand_identity JSONField to BrandProfile
"""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('brands', '0001_initial'),  # Make sure to update this to the actual last migration
    ]

    operations = [
        migrations.AddField(
            model_name='brandprofile',
            name='brand_identity',
            field=models.JSONField(default=dict),
        ),
    ]