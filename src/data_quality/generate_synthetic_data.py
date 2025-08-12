import os
import random
import csv
from datetime import datetime, timedelta

CURRENCIES = ["GBP","EUR","USD","NGN","ZAR","INR","usd"," xyz "]
LAWS = ["England & Wales","Scotland","Delaware","New York","Nigeria"]
STATUS = ["Active","Expired","Draft","Signed"]

random.seed(42)


def make_row(i):
    base = datetime(2023,1,1) + timedelta(days=random.randint(0, 600))
    eff = base.strftime('%Y-%m-%d')
    end = (base + timedelta(days=random.randint(-120, 720))).strftime('%Y-%m-%d')
    amount = round(random.uniform(1000, 250000), 2)
    # inject issues
    email = random.choice([
        f"contact{i}@example.com",
        f" user{i}@bad email .com ",
        None
    ])
    ccy = random.choice(CURRENCIES)
    dpa = random.choice(["Y","N","y","n"," "])
    law = random.choice(LAWS)
    status = random.choice(STATUS)
    return [
        f"C-{100000+i}",
        f"PartyA_{random.randint(1, 300)}",
        f"PartyB_{random.randint(1, 300)}",
        eff,
        end,
        law,
        amount,
        ccy,
        dpa,
        email,
        status,
        (base + timedelta(days=random.randint(-30, 365))).strftime('%Y-%m-%d')
    ]


def write_csv(path, n=500):
    headers = [
        "contract_id","party_a","party_b","effective_date","end_date","governing_law",
        "amount","currency","dpa_present","contact_email","status","review_due_date"
    ]
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(headers)
        for i in range(n):
            w.writerow(make_row(i))

if __name__ == '__main__':
    out = os.environ.get('OUT','assets/sample_contract_register.csv')
    n = int(os.environ.get('N','500'))
    write_csv(out, n)
    print(f"Wrote {n} rows to {out}")
