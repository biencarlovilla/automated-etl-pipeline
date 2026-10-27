import pandas as pd

# Extract: Load the original retail dataset
df = pd.read_csv("data/online_retail.csv")

# Inspect the dataset
print("Dataset Shape:", df.shape)
print("\nColumn Names:")
print(df.columns.tolist())

print("\nFirst 5 Rows:")
print(df.head())

# Assess data quality before transformation
print("\n--- DATA QUALITY REPORT ---")

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())

print("\nData Types:")
print(df.dtypes)

print("\nInvalid Quantities (<= 0):")
print((df["Quantity"] <= 0).sum())

print("\nInvalid Prices (<= 0):")
print((df["UnitPrice"] <= 0).sum())

# Transform: Create a working copy
clean_df = df.copy()

# Inspect original date format
print("Original date examples:")
print(df["InvoiceDate"].head(5).tolist())

# Convert invoice dates to datetime
clean_df["InvoiceDate"] = pd.to_datetime(
    clean_df["InvoiceDate"],
    format="%m/%d/%y %H:%M",
    errors="coerce"
)

print("Invalid dates:", clean_df["InvoiceDate"].isna().sum())

# Convert customer IDs to nullable integers
clean_df["CustomerID"] = clean_df["CustomerID"].astype("Int64")

# Verify transformations
print("\n--- TRANSFORMATION RESULTS ---")
print(clean_df[["InvoiceDate", "CustomerID"]].dtypes)

print("\nFirst 5 Transformed Records:")
print(clean_df[["InvoiceDate", "CustomerID"]].head())

# Remove exact duplicate records
print("\n--- DUPLICATE CLEANING ---")

rows_before = len(clean_df)

clean_df = clean_df.drop_duplicates().copy()

rows_after = len(clean_df)

print("Rows Before:", rows_before)
print("Duplicates Removed:", rows_before - rows_after)
print("Rows After:", rows_after)
print("Remaining Duplicates:", clean_df.duplicated().sum())

# Handle missing values
print("\n--- MISSING VALUE CLEANING ---")

# Count missing values before cleaning
print("Missing Descriptions Before:",
      clean_df["Description"].isna().sum())

print("Missing CustomerIDs:",
      clean_df["CustomerID"].isna().sum())

# Fill missing product descriptions
clean_df["Description"] = clean_df["Description"].fillna(
    "Unknown Product"
)

# Verify results
print("Missing Descriptions After:",
      clean_df["Description"].isna().sum())

print("Total Rows After Cleaning:", len(clean_df))

# Classify transactions
print("\n--- TRANSACTION CLASSIFICATION ---")

clean_df["TransactionType"] = "Sale"

clean_df.loc[
    clean_df["Quantity"] < 0,
    "TransactionType"
] = "Return"

clean_df.loc[
    clean_df["Quantity"] == 0,
    "TransactionType"
] = "Zero Quantity"

# Calculate transaction amount
clean_df["TotalAmount"] = (
    clean_df["Quantity"] * clean_df["UnitPrice"]
).round(2)

# Display classification results
print("\nTransaction Types:")
print(clean_df["TransactionType"].value_counts())

print("\nZero or Negative Prices:")
print((clean_df["UnitPrice"] <= 0).sum())

print("\nFirst 5 Transactions:")
print(clean_df[
    ["InvoiceNo", "Quantity", "UnitPrice",
     "TransactionType", "TotalAmount"]
].head())

# Validate transformed dataset
print("\n--- FINAL DATA VALIDATION ---")

print("Total Records:", len(clean_df))
print("Duplicate Records:", clean_df.duplicated().sum())
print("Invalid Dates:", clean_df["InvoiceDate"].isna().sum())
print("Missing Descriptions:", clean_df["Description"].isna().sum())
print("Missing Customer IDs:", clean_df["CustomerID"].isna().sum())

print("\nTransaction Amount Summary:")
print(clean_df["TotalAmount"].describe())

# Connect to PostgreSQL
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME")
)

engine = create_engine(database_url)

# Test database connection
print("\n--- DATABASE CONNECTION TEST ---")

with engine.connect() as connection:
    result = connection.execute(text("SELECT current_database(), version();"))
    database_name, postgres_version = result.fetchone()

    print("Connection: Successful")
    print("Database:", database_name)
    print("PostgreSQL:", postgres_version.split(",")[0])

    # Load transformed data into PostgreSQL
    print("\n--- LOADING DATA INTO POSTGRESQL ---")

    clean_df.to_sql(
        name="retail_transactions",
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=5000,
        method="multi"
    )

    print("Data Load: Successful")
    print("Records Loaded:", len(clean_df))
    print("Target Table: retail_transactions")