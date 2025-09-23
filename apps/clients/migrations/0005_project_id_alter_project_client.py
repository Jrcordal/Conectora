
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0004_project_clientprofile_active_projects_and_more'),
    ]

    operations = [
        # 1) Quitar el PK de 'client' (pasa a FK normal)
        migrations.AlterField(
            model_name='project',
            name='client',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='clientproject',
                to='clients.clientprofile',
            ),
        ),
        # 2) Añadir el nuevo PK 'id'
        migrations.AddField(
            model_name='project',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]

