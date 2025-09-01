import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# This script generates a synthetic dataset of 25,000 compliance documents.
# The generation process uses a rule-based and template-driven approach to simulate
# realistic legal and compliance documents, addressing the scarcity of public datasets.
# The generated data includes a risk level distribution (HighRisk, MediumRisk, LowRisk)
# and is split into training, validation, and testing sets (70/15/15).

import random
import csv
from datetime import datetime, timedelta
import pandas as pd
from sklearn.model_selection import train_test_split
# from src.utils.logging_config import get_logger

# logger = get_logger(__name__)

CURRENCIES = ["GBP", "EUR", "USD", "NGN", "ZAR", "INR", "usd", " xyz "]
LAWS = ["England & Wales", "Scotland", "Delaware", "New York", "Nigeria"]
STATUS = ["Active", "Expired", "Draft", "Signed"]

random.seed(42)

def get_risk_level(row_data):
    """
    Determines the risk level of a document based on its attributes.
    """
    issues = 0
    if row_data['currency'] not in ["GBP", "EUR", "USD"]:
        issues += 1
    if row_data['dpa_present'].strip().upper() not in ['Y', 'N']:
        issues += 1
    if not row_data['contact_email'] or " " in row_data['contact_email']:
        issues += 1
    if row_data['status'] == "Expired":
        issues += 2

    if issues >= 3:
        return "HighRisk"
    elif issues >= 1:
        return "MediumRisk"
    else:
        return "LowRisk"

def make_row(i):
    base = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 600))
    eff = base.strftime("%Y-%m-%d")
    end = (base + timedelta(days=random.randint(-120, 720))).strftime("%Y-%m-%d")
    amount = round(random.uniform(1000, 250000), 2)
    # inject issues
    email = random.choice([f"contact{i}@example.com", f" user{i}@bad email .com ", None])
    ccy = random.choice(CURRENCIES)
    dpa = random.choice(["Y", "N", "y", "n", " "])
    law = random.choice(LAWS)
    status = random.choice(STATUS)
    
    row_data = {
        "contract_id": f"C-{100000+i}",
        "party_a": f"PartyA_{random.randint(1, 300)}",
        "party_b": f"PartyB_{random.randint(1, 300)}",
        "effective_date": eff,
        "end_date": end,
        "governing_law": law,
        "amount": amount,
        "currency": ccy,
        "dpa_present": dpa,
        "contact_email": email,
        "status": status,
        "review_due_date": (base + timedelta(days=random.randint(-30, 365))).strftime("%Y-%m-%d"),
    }
    row_data['risk_level'] = get_risk_level(row_data)
    
    return list(row_data.values())


def generate_data(n=25000):
    """
    Generates a dataframe with n rows of synthetic data.
    """
    headers = [
        "contract_id",
        "party_a",
        "party_b",
        "effective_date",
        "end_date",
        "governing_law",
        "amount",
        "currency",
        "dpa_present",
        "contact_email",
        "status",
        "review_due_date",
        "risk_level"
    ]
    data = [make_row(i) for i in range(n)]
    df = pd.DataFrame(data, columns=headers)
    return df


if __name__ == "__main__":
    output_dir = "assets"
    os.makedirs(output_dir, exist_ok=True)
    
    n = 25000
    df = generate_data(n)
    
    train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)
    
    train_path = os.path.join(output_dir, "train.csv")
    val_path = os.path.join(output_dir, "validation.csv")
    test_path = os.path.join(output_dir, "test.csv")
    
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    # logger.info(f"Wrote {len(train_df)} rows to {train_path}")
    # logger.info(f"Wrote {len(val_df)} rows to {val_path}")
    # logger.info(f"Wrote {len(test_df)} rows to {test_path}")
    
    risk_distribution = df['risk_level'].value_counts(normalize=True)
    # logger.info(f"Risk Level Distribution:\n{risk_distribution}")
    print(f"Wrote {len(train_df)} rows to {train_path}")
    print(f"Wrote {len(val_df)} rows to {val_path}")
    print(f"Wrote {len(test_df)} rows to {test_path}")
    print(f"Risk Level Distribution:\n{risk_distribution}")