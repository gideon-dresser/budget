import main

df = main.read_and_clean_csv()
transactions = main.TransactionFactory.from_csv()

# Test 3: Inspect individual transactions
# print("\nFirst 3 transactions:")
for i, t in enumerate(transactions[:20]):
    print(f"{i + 1}. Date: {t.date}, Description: {t.description}, Amount: ${t.amount}, Category: {t.category}")

# Test 4: Test categorization
categorizer = main.TransactionCategorizer()
uncategorized = []

for t in transactions[:5]:
    if not categorizer.categorize(t):
        uncategorized.append(t)

print(f"\nAuto-categorized: {len(transactions) - len(uncategorized)}/{len(transactions)}")
print(f"Need manual review: {len(uncategorized)}")

# Prompt for uncategorized transactions
if uncategorized:
    print("\n" + "=" * 50)
    review = input(f"Review {len(uncategorized)} uncategorized transactions? (y/n): ")

    if review.lower() == 'y':
        for t in uncategorized:
            main.prompt_for_categorization(t, categorizer)