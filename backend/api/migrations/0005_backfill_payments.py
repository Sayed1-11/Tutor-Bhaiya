# Generated manually to backfill Payment records for existing course enrollments.

import uuid
from django.db import migrations

def backfill_payments(apps, schema_editor):
    Enrollment = apps.get_model('api', 'Enrollment')
    Payment = apps.get_model('api', 'Payment')
    for enrollment in Enrollment.objects.all():
        if enrollment.course:
            # Check if a payment already exists for this enrollment
            if not Payment.objects.filter(user=enrollment.user, course=enrollment.course).exists():
                Payment.objects.create(
                    user=enrollment.user,
                    course=enrollment.course,
                    amount=enrollment.course.price,
                    payment_method='bkash',
                    transaction_id=f"BKX{uuid.uuid4().hex[:8].upper()}",
                    status='completed'
                )

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_studentassignment_is_passed_studentassignment_status_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_payments),
    ]
