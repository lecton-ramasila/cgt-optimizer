from app import create_app
from models import db, User, Portfolio, Position, Lot
from config import PORTFOLIO, COUNTRY

def seed():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create a default user
        user = User(username="default_user", email="user@example.com")
        db.session.add(user)
        db.session.commit()

        # Create the main portfolio
        portfolio = Portfolio(name="Main Portfolio", country=COUNTRY, owner=user)
        db.session.commit()

        # Migrate positions and lots
        for ticker, info in PORTFOLIO.items():
            pos = Position(
                ticker=ticker,
                name=info["name"],
                platform=info["platform"],
                asset_type=info["type"],
                currency=info.get("currency", "USD"),
                portfolio=portfolio
            )
            db.session.add(pos)
            db.session.commit()

            for lot_data in info["lots"]:
                date, cost, units = lot_data
                lot = Lot(
                    date=date,
                    cost_per_share=cost,
                    units=units,
                    position=pos
                )
                db.session.add(lot)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed()
