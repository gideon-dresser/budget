import pandas as pd
import json
import os

def read_and_clean_csv():
    df = pd.read_csv('statement.csv', skiprows=2)
    df['date'] = pd.to_datetime(df['Transaction Date'], format='%Y%m%d')
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['amount'] = df['Transaction Amount']
    return df

def prompt_for_categorization(transaction, categorizer):
    """Prompt user to manually categorize a transaction"""
    # print("\n" + "=" * 50)
    print("UNCATEGORIZED TRANSACTION:")
    print(f"Date: {transaction.date.strftime('%Y-%m-%d')}")
    print(f"Description: {transaction.description}")
    print(f"Amount: ${transaction.amount:.2f}")

    category = input("Enter category (or 'skip' to leave uncategorized): ").strip()

    if category.lower() != 'skip' and category:
        categorizer.learn_from_manual_entry(transaction.description, category)
        transaction.categorize(category)
        print(f"✓ Learned rule: '{transaction.description}' → '{category}'")
        return True
    return False

class Transaction:
    def __init__(self, date, description, amount, category=None):
        self.date = date
        self.description = description
        self.amount = amount
        self.category = category

    def categorize(self, category):
        self.category = category

class TransactionFactory:
    @staticmethod
    def from_csv():
        df = read_and_clean_csv()
        transactions = []
        for _, row in df.iterrows():
            transactions.append(Transaction(
                date=row['date'],
                description=row['Description'],
                amount=row['amount']
            ))
        return transactions


class TransactionCategorizer:
    def __init__(self, rules_file='categorization_rules.json'):
        self.rules_file = rules_file
        self.rules = self._load_rules()

    def _load_rules(self):
        """Load rules from JSON file, or return defaults if file doesn't exist"""
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not read {self.rules_file}, using defaults")
                return {"safeway": "Groceries"}
        else:
            # First time running - create with defaults
            return {"safeway": "Groceries"}

    def _save_rules(self):
        """Save rules to JSON file"""
        with open(self.rules_file, 'w') as f:
            json.dump(self.rules, f, indent=2)
        print(f"Rules saved to {self.rules_file}")

    def add_rule(self, keyword, category):
        self.rules[keyword.lower()] = category
        self._save_rules()  # Save immediately after adding

    def categorize(self, transaction):
        description_lower = transaction.description.lower()
        for keyword, category in self.rules.items():
            if keyword in description_lower:
                transaction.categorize(category)
                return category
        return None

    def learn_from_manual_entry(self, description, category):
        # Extract key merchant name and save rule
        self.add_rule(description, category)