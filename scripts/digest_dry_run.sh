#!/usr/bin/env bash
# digest_dry_run.sh - Run weekly digest in dry-run mode
# Usage: ./scripts/digest_dry_run.sh [--email user@example.com]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}📧 StepWise Weekly Digest - Dry Run${NC}"
echo ""

# Export dev environment variables
export API_ACCESS_KEY="${API_ACCESS_KEY:-dev-test-key}"
export EMAIL_PROVIDER="${EMAIL_PROVIDER:-console}"
export DATABASE_URL="${DATABASE_URL:-sqlite:///./stepwise.db}"

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "   EMAIL_PROVIDER: $EMAIL_PROVIDER"
echo "   DATABASE_URL: $DATABASE_URL"
echo ""

cd "$PROJECT_ROOT/backend"

# Check if script exists
if [ ! -f "scripts/send_weekly_digest.py" ]; then
    echo -e "${YELLOW}⚠️  Weekly digest script not found at backend/scripts/send_weekly_digest.py${NC}"
    echo ""
    echo "Creating placeholder script..."

    mkdir -p scripts
    cat > scripts/send_weekly_digest.py << 'DIGEST_SCRIPT'
#!/usr/bin/env python3
"""Weekly digest email sender script.

Usage:
    python scripts/send_weekly_digest.py --dry-run
    python scripts/send_weekly_digest.py --email parent@example.com
    python scripts/send_weekly_digest.py --start-date 2025-01-01
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone

def main():
    parser = argparse.ArgumentParser(description="Send weekly digest emails")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    parser.add_argument("--email", type=str, help="Send to specific email only")
    parser.add_argument("--start-date", type=str, help="Week start date (YYYY-MM-DD)")

    args = parser.parse_args()

    # Calculate date range
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        # Default to last Monday
        today = datetime.now(timezone.utc)
        start_date = today - timedelta(days=today.weekday() + 7)

    end_date = start_date + timedelta(days=7)

    print(f"📅 Period: {start_date.date()} to {end_date.date()}")
    print(f"🔍 Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    if args.email:
        print(f"📧 Target: {args.email}")
    print()

    # Import after path setup
    sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from backend.database.engine import Base
        from backend.models.session import HintSession
        from backend.services.weekly_digest import WeeklyDigestGenerator
        from backend.services.email_service import EmailService
        import os

        # Create database connection
        db_url = os.getenv("DATABASE_URL", "sqlite:///./stepwise.db")
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()

        # Get unique parent emails with sessions in this period
        query = db.query(HintSession.parent_email).filter(
            HintSession.parent_email.isnot(None),
            HintSession.started_at >= start_date,
            HintSession.started_at < end_date,
        ).distinct()

        if args.email:
            query = query.filter(HintSession.parent_email == args.email)

        emails = [row[0] for row in query.all()]

        print(f"📬 Found {len(emails)} recipient(s)")
        print()

        if not emails:
            print("No recipients found for this period.")
            return 0

        generator = WeeklyDigestGenerator()
        email_service = EmailService()

        for email in emails:
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"📧 {email}")

            digest = generator.generate_weekly_digest(db, email, start_date, end_date)

            if digest:
                print(f"   Sessions: {digest['total_sessions']}")
                print(f"   Completed: {digest['completed_sessions']}")
                print(f"   Performance: {digest['performance_level']}")

                if not args.dry_run:
                    success = email_service.send_weekly_digest(
                        recipient_email=email,
                        digest_data=digest,
                        week_start_date=start_date.strftime("%Y-%m-%d"),
                        db=db,
                    )
                    print(f"   Sent: {'✓' if success else '✗'}")
                else:
                    print(f"   [DRY RUN - not sent]")
            else:
                print(f"   No data for this period")
            print()

        db.close()
        print("✅ Done!")
        return 0

    except ImportError as e:
        print(f"⚠️  Import error: {e}")
        print("Make sure you're running from the backend directory with dependencies installed.")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
DIGEST_SCRIPT

    echo -e "${GREEN}✓ Created backend/scripts/send_weekly_digest.py${NC}"
    echo ""
fi

echo -e "${GREEN}🚀 Running weekly digest in dry-run mode...${NC}"
echo ""

# Run the digest script
python3 scripts/send_weekly_digest.py --dry-run "$@"
