#!/usr/bin/env python
"""
Create superuser and test data for development.
Run: python manage.py shell < setup_dev_data.py
Or: python manage.py runscript setup_dev_data (if django-extensions installed)
Or from shell: exec(open('setup_dev_data.py').read())

Creates:
- 1 administrator (admin@test.com / test123)
- 1 company user (company@test.com / test123)
- 3 institutions linked to that company
- 10 sample collection requests
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vuvoz.settings')
django.setup()

from decimal import Decimal
from django.contrib.auth import get_user_model
from collection.models import CompanyProfile, InstitutionProfile, CollectionRequest

User = get_user_model()

ADMIN_EMAIL = 'admin@test.com'
COMPANY_EMAIL = 'company@test.com'


def run():
    from scripts.dev_env import get_dev_test_password

    dev_password = get_dev_test_password()
    # Administrator
    admin_user, admin_created = User.objects.get_or_create(
        username=ADMIN_EMAIL,
        defaults={
            'email': ADMIN_EMAIL,
            'role': User.Role.ADMIN,
            'is_active': True,
        },
    )
    if admin_created:
        admin_user.set_password(dev_password)
        admin_user.save()
        print(f"Created administrator: {ADMIN_EMAIL}")
    else:
        if admin_user.role != User.Role.ADMIN:
            admin_user.role = User.Role.ADMIN
            admin_user.save()
            print(f"Updated user to administrator: {ADMIN_EMAIL}")
        else:
            print(f"Administrator exists: {ADMIN_EMAIL}")

    # Company
    company_user, created = User.objects.get_or_create(
        username=COMPANY_EMAIL,
        defaults={
            'email': COMPANY_EMAIL,
            'role': User.Role.COMPANY,
            'is_active': True,
        },
    )
    if created:
        company_user.set_password(dev_password)
        company_user.save()
        print(f"Created company user: {COMPANY_EMAIL}")
    else:
        print(f"Company user exists: {COMPANY_EMAIL}")

    profile, _ = CompanyProfile.objects.get_or_create(
        user=company_user,
        defaults={
            'company_name': 'Test Collection Company',
            'address': '100 Company Street',
            'contact_phone': '+1 555 000 0001',
            'contact_email': COMPANY_EMAIL,
        },
    )
    if not profile.company_name == 'Test Collection Company':
        profile.company_name = 'Test Collection Company'
        profile.save()

    # Institutions
    institutions_data = [
        {'email': 'school1@test.com', 'name': 'Green Valley School', 'type': 'school'},
        {'email': 'school2@test.com', 'name': 'Riverside Academy', 'type': 'school'},
        {'email': 'office@test.com', 'name': 'City Office Building', 'type': 'office'},
    ]
    institutions = []
    for data in institutions_data:
        user, u_created = User.objects.get_or_create(
            username=data['email'],
            defaults={
                'email': data['email'],
                'role': User.Role.INSTITUTION,
                'is_active': True,
            },
        )
        if u_created:
            user.set_password(dev_password)
            user.save()
            print(f"Created institution user: {data['email']}")

        inst, i_created = InstitutionProfile.objects.get_or_create(
            user=user,
            defaults={
                'parent_company': profile,
                'institution_name': data['name'],
                'address': f'Address for {data["name"]}',
                'contact_person': 'Contact Person',
                'phone': '+1 555 000 0002',
                'email': data['email'],
                'institution_type': data['type'],
            },
        )
        if i_created:
            print(f"Created institution: {data['name']}")
        # Ensure company link is set (verify institution -> company)
        if inst.parent_company_id != profile.id:
            inst.parent_company = profile
            inst.save()
            print(f"Linked institution {inst.institution_name} to company {profile.company_name}")
        institutions.append(inst)

    # Verify company link: each created institution must belong to the test company
    for inst in institutions:
        assert inst.parent_company_id == profile.id, f"Institution {inst.institution_name} not linked to company"
    linked_count = InstitutionProfile.objects.filter(parent_company=profile).count()
    print(f"Verified company link: {len(institutions)} institutions in this run linked to {profile.company_name} (total linked to company: {linked_count})")

    # Sample requests (create only if none exist)
    existing = CollectionRequest.objects.filter(receiving_company=profile).count()
    if existing >= 10:
        print("Sample requests already exist.")
    else:
        statuses = [CollectionRequest.Status.NEW, CollectionRequest.Status.ACCEPTED, CollectionRequest.Status.COMPLETED]
        weights = [Decimal('25.50'), Decimal('40.00'), Decimal('15.25'), Decimal('100.00'), Decimal('33.33')]
        for i in range(10):
            inst = institutions[i % len(institutions)]
            status = statuses[i % 3]
            CollectionRequest.objects.create(
                institution=inst,
                receiving_company=profile,
                status=status,
                paper_weight_kg=weights[i % len(weights)],
                comment=f'Sample request #{i+1}',
            )
        print("Created 10 sample collection requests.")

    print("\nDone. Test data logins:")
    print(f"  Administrator: {ADMIN_EMAIL} / {dev_password}")
    print(f"  Company:       {COMPANY_EMAIL} / {dev_password}")
    print(f"  Institution:   school1@test.com / {dev_password} (or school2@test.com, office@test.com)")


if __name__ == '__main__':
    run()
