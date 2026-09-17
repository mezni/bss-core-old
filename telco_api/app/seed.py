import random
from datetime import datetime, timedelta
from faker import Faker
from pwdlib import PasswordHash

from app.database import SessionLocal, engine
import app.models as models

fake = Faker()
password_hash = PasswordHash.recommended()

# Fixed hash for "password" to speed up seeding
FIXED_PASSWORD_HASH = password_hash.hash("password")


def run_seed():
    """Reset and seed the SQLite database with custom target metrics."""
    print("Resetting database tables...")
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Starting data seeding process...")

        # ----------------------------------------------------
        # 1. SYSTEM USERS (Target: 10, Password: "password")
        # ----------------------------------------------------
        users = []
        for i in range(10):
            # First 2 users are Admins, remaining 8 are CSRs
            role = models.UserRole.ADMIN if i < 2 else models.UserRole.CSR
            user = models.UserModel(
                username=f"user_{i+1}",
                hashed_password=FIXED_PASSWORD_HASH,
                role=role,
                is_active=True,
            )
            db.add(user)
            users.append(user)
        db.flush()
        print("✔ Created 10 System Users (user_1 to user_10, password='password').")

        # ----------------------------------------------------
        # 2. SUBSCRIBERS & TELECOM LINES (Target: 10 Subscribers)
        # ----------------------------------------------------
        subscribers = []
        lines = []
        account_types = [models.AccountType.PREPAID, models.AccountType.POSTPAID]

        for i in range(10):
            sub = models.SubscriberModel(
                name=fake.name(),
                email=fake.unique.email(),
                account_type=random.choice(account_types),
            )
            db.add(sub)
            db.flush()
            subscribers.append(sub)

            # Assign 1 to 2 telecom lines per subscriber
            for _ in range(random.randint(1, 2)):
                msisdn = f"+1{fake.numeric_regex(pattern='##########')}"
                iccid = f"8901410{fake.numeric_regex(pattern='#############')}"
                line = models.TelecomLineModel(
                    msisdn=msisdn,
                    iccid=iccid,
                    status=models.LineStatus.ACTIVE,
                    data_usage_gb=0.0,
                    subscriber_id=sub.id,
                )
                db.add(line)
                lines.append(line)
        db.flush()
        print(f"✔ Created 10 Subscribers and {len(lines)} active lines.")

        # ----------------------------------------------------
        # 3. DEVICES (Target: 10 Devices)
        # ----------------------------------------------------
        device_types = list(models.DeviceType)
        brands_models = [
            ("Apple", "iPhone 15 Pro"),
            ("Samsung", "Galaxy S24 Ultra"),
            ("Google", "Pixel 8 Pro"),
            ("Netgear", "Nighthawk M6 5G Router"),
            ("Motorola", "Edge 50"),
            ("Lenovo", "Tab P12"),
            ("Garmin", "Forerunner 965 LTE"),
        ]

        for i in range(10):
            sub = subscribers[i]
            assigned_line = lines[i] if i < len(lines) else None
            brand, model_name = random.choice(brands_models)

            device = models.DeviceModel(
                imei_esn=fake.numeric_regex(pattern="###############"),
                brand=brand,
                model_name=model_name,
                device_type=random.choice(device_types),
                status=models.DeviceStatus.ACTIVE,
                purchase_date=datetime.utcnow() - timedelta(days=random.randint(10, 365)),
                subscriber_id=sub.id,
                assigned_msisdn=assigned_line.msisdn if assigned_line else None,
            )
            db.add(device)
        db.flush()
        print("✔ Created 10 Devices mapped to subscribers.")

        # ----------------------------------------------------
        # 4. INVOICES / BILLS (Target: 50 Invoices)
        # ----------------------------------------------------
        invoice_statuses = [
            models.InvoiceStatus.PAID,
            models.InvoiceStatus.UNPAID,
            models.InvoiceStatus.OVERDUE,
        ]

        for _ in range(50):
            sub = random.choice(subscribers)
            created_date = datetime.utcnow() - timedelta(days=random.randint(1, 180))

            invoice = models.InvoiceModel(
                subscriber_id=sub.id,
                amount=round(random.uniform(29.99, 199.99), 2),
                currency="USD",
                status=random.choice(invoice_statuses),
                due_date=created_date + timedelta(days=30),
                created_at=created_date,
            )
            db.add(invoice)
        db.flush()
        print("✔ Created 50 Invoices across subscribers.")

        # ----------------------------------------------------
        # 5. USAGE RECORDS / CDRs (Target: 2,000 Records)
        # ----------------------------------------------------
        usage_configs = [
            (models.UsageType.DATA, "GB", 0.05, 4.5),
            (models.UsageType.VOICE, "Minutes", 1.0, 35.0),
            (models.UsageType.SMS, "Messages", 1.0, 1.0),
        ]

        for _ in range(2000):
            line = random.choice(lines)
            u_type, u_unit, min_qty, max_qty = random.choices(
                usage_configs, weights=[0.6, 0.25, 0.15]
            )[0]
            quantity = round(random.uniform(min_qty, max_qty), 2)
            timestamp = datetime.utcnow() - timedelta(minutes=random.randint(1, 43200))  # Last 30 days

            record = models.UsageRecordModel(
                msisdn=line.msisdn,
                type=u_type,
                quantity=quantity,
                unit=u_unit,
                timestamp=timestamp,
            )
            db.add(record)

            # Accumulate data usage directly on the line record
            if u_type == models.UsageType.DATA:
                line.data_usage_gb = round(line.data_usage_gb + quantity, 2)

        db.commit()
        print("✔ Created 2,000 Usage CDR Records.")
        print("\n🎉 Database successfully populated with target dataset!")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()