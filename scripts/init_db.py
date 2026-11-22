from backend.database.connection import Base, engine

# Import models so SQLAlchemy registers all tables
from backend.database import models


def initialize_database():

    print("\nInitializing AIDoc Database...")

    try:

        Base.metadata.create_all(bind=engine)

        print("\nDatabase initialized successfully!")

        print("\nCreated Tables:")

        for table in Base.metadata.sorted_tables:
            print(f" - {table.name}")

    except Exception as error:

        print("\nDatabase initialization failed!")

        print(error)


if __name__ == "__main__":

    initialize_database()