# Generated manually to add country and currency fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='country',
            field=models.CharField(choices=[('US', 'United States'), ('CA', 'Canada'), ('GB', 'United Kingdom'), ('AU', 'Australia'), ('DE', 'Germany'), ('FR', 'France'), ('IT', 'Italy'), ('ES', 'Spain'), ('NL', 'Netherlands'), ('BE', 'Belgium'), ('CH', 'Switzerland'), ('AT', 'Austria'), ('SE', 'Sweden'), ('NO', 'Norway'), ('DK', 'Denmark'), ('FI', 'Finland'), ('IE', 'Ireland'), ('PT', 'Portugal'), ('IN', 'India'), ('SG', 'Singapore'), ('HK', 'Hong Kong'), ('JP', 'Japan'), ('CN', 'China'), ('BR', 'Brazil'), ('MX', 'Mexico'), ('NZ', 'New Zealand'), ('ZA', 'South Africa')], default='US', max_length=2),
        ),
        migrations.AddField(
            model_name='company',
            name='currency',
            field=models.CharField(choices=[('USD', 'US Dollar ($)'), ('EUR', 'Euro (€)'), ('GBP', 'British Pound (£)'), ('CAD', 'Canadian Dollar (C$)'), ('AUD', 'Australian Dollar (A$)'), ('CHF', 'Swiss Franc (CHF)'), ('SEK', 'Swedish Krona (kr)'), ('NOK', 'Norwegian Krone (kr)'), ('DKK', 'Danish Krone (kr)'), ('JPY', 'Japanese Yen (¥)'), ('CNY', 'Chinese Yuan (¥)'), ('INR', 'Indian Rupee (₹)'), ('SGD', 'Singapore Dollar (S$)'), ('HKD', 'Hong Kong Dollar (HK$)'), ('BRL', 'Brazilian Real (R$)'), ('MXN', 'Mexican Peso ($)'), ('NZD', 'New Zealand Dollar (NZ$)'), ('ZAR', 'South African Rand (R)')], default='USD', max_length=3),
        ),
    ]