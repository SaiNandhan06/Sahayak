"""
data_generation.py
------------------
Generates ~20 synthetic documents covering Indian personal finance topics
and stores them in a persistent ChromaDB vector database using
nomic-embed-text embeddings via Ollama.

Usage:
    python data_generation.py
"""

import os
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL

# ── Synthetic Documents ───────────────────────────────────────────────────────
DOCUMENTS = [
    # 1-6 · Spending Categories
    Document(
        page_content=(
            "Spending Category: Food & Dining\n"
            "This category includes expenses at restaurants, cafes, food delivery apps "
            "(Swiggy, Zomato), groceries (BigBasket, Blinkit), tea stalls, and street food. "
            "Common merchant names: Swiggy, Zomato, BigBasket, Dominos, McDonald's, KFC, "
            "Starbucks, local dhabas. Typical range: ₹50 – ₹3,000 per transaction. "
            "Monthly average for a city-dweller: ₹5,000 – ₹12,000."
        ),
        metadata={"category": "spending_categories", "topic": "food_dining"},
    ),
    Document(
        page_content=(
            "Spending Category: Travel & Transportation\n"
            "Covers metro, bus, auto-rickshaw, cab rides (Ola, Uber, Rapido), flight tickets, "
            "train tickets (IRCTC), fuel at petrol pumps, and toll charges. "
            "Common merchant names: Ola, Uber, Rapido, IRCTC, IndiGo, SpiceJet, BEST, BMTC. "
            "Monthly average for a working professional: ₹2,000 – ₹8,000."
        ),
        metadata={"category": "spending_categories", "topic": "travel"},
    ),
    Document(
        page_content=(
            "Spending Category: Utilities & Bills\n"
            "Includes electricity bills (BESCOM, MSEDCL), water bills, gas cylinder booking "
            "(HP Gas, Bharat Gas, Indane), internet/broadband (Jio, Airtel, ACT), mobile "
            "recharge, and OTT subscriptions (Netflix, Amazon Prime, Hotstar). "
            "Monthly range: ₹1,500 – ₹5,000."
        ),
        metadata={"category": "spending_categories", "topic": "utilities"},
    ),
    Document(
        page_content=(
            "Spending Category: Shopping\n"
            "Includes online shopping (Amazon, Flipkart, Meesho, Myntra, Nykaa) and offline "
            "retail (clothing, electronics, home goods). Often shows as EMI deductions from "
            "bank accounts. Festive season (Diwali, Dussehra) typically sees 2-3x spike. "
            "Monthly range: ₹1,000 – ₹20,000."
        ),
        metadata={"category": "spending_categories", "topic": "shopping"},
    ),
    Document(
        page_content=(
            "Spending Category: Health & Medical\n"
            "Covers pharmacy purchases (Apollo, MedPlus, 1mg), doctor consultation fees, "
            "diagnostic test charges (Dr Lal Pathlabs, SRL), gym memberships, yoga classes, "
            "and health insurance premiums. Monthly range: ₹500 – ₹5,000 (excluding insurance)."
        ),
        metadata={"category": "spending_categories", "topic": "health"},
    ),
    Document(
        page_content=(
            "Spending Category: Entertainment & Leisure\n"
            "Covers movie tickets (BookMyShow, PVR, INOX), gaming (Steam, Google Play), "
            "amusement parks, concerts, and hobby expenses. Monthly range: ₹500 – ₹3,000."
        ),
        metadata={"category": "spending_categories", "topic": "entertainment"},
    ),

    # 7-10 · SMS Alert Examples
    Document(
        page_content=(
            "SMS Format: HDFC Bank Debit Alert\n"
            "Your HDFC Bank Account XXXX1234 has been debited with INR 450.00 on 21-Feb-26. "
            "Info: SWIGGY. Available Bal: INR 12,340.50. Not you? Call 1800-266-4332 or SMS "
            "BLOCK to 5676712. -HDFC Bank\n\n"
            "Parsed fields: bank=HDFC, account_last4=1234, amount=450.00, "
            "merchant=SWIGGY, date=2026-02-21, category=Food & Dining."
        ),
        metadata={"category": "sms_examples", "bank": "HDFC"},
    ),
    Document(
        page_content=(
            "SMS Format: SBI Debit Alert\n"
            "Your account XXXX5678 has been debited by Rs.1200.00 on date 21Feb26 trf to "
            "IRCTC. Avbl Bal Rs.8560.75. If not done by you, call 1800-11-2211. -SBI\n\n"
            "Parsed fields: bank=SBI, account_last4=5678, amount=1200.00, "
            "merchant=IRCTC, date=2026-02-21, category=Travel & Transportation."
        ),
        metadata={"category": "sms_examples", "bank": "SBI"},
    ),
    Document(
        page_content=(
            "SMS Format: ICICI Bank UPI Credit\n"
            "Rs.500.00 received in your ICICI Bank A/c XXXX9012 from PhonePe on 20-Feb-26 "
            "via UPI (Ref No. 612345678901). Available balance: Rs.24,150.30. -ICICI Bank\n\n"
            "Parsed fields: bank=ICICI, type=credit, amount=500.00, source=PhonePe, "
            "date=2026-02-20."
        ),
        metadata={"category": "sms_examples", "bank": "ICICI"},
    ),
    Document(
        page_content=(
            "SMS Format: UPI Payment Confirmation (Google Pay / PhonePe)\n"
            "Rs.350 paid to +91-9876543210 (Raj Kirana Store) via Google Pay on 21 Feb 2026 "
            "at 09:15 AM. UPI Ref: 1234567890. If not done by you, report at g.co/upi/help.\n\n"
            "Parsed fields: app=GooglePay, amount=350, recipient=Raj Kirana Store, "
            "date=2026-02-21, category=Food & Dining (grocery)."
        ),
        metadata={"category": "sms_examples", "bank": "UPI"},
    ),

    # 11-13 · Budgeting Strategies
    Document(
        page_content=(
            "Budgeting Strategy: 50/30/20 Rule\n"
            "Allocate 50% of after-tax income to Needs (rent, groceries, utilities, EMIs), "
            "30% to Wants (dining out, entertainment, shopping, vacations), and 20% to "
            "Savings & Investments (FD, mutual funds, SIP, emergency fund). "
            "Example for Rs.50,000/month salary: Needs Rs.25,000 | Wants Rs.15,000 | Savings Rs.10,000. "
            "This rule is recommended by most Indian financial planners as a starter budget."
        ),
        metadata={"category": "budgeting", "strategy": "50_30_20"},
    ),
    Document(
        page_content=(
            "Budgeting Strategy: Zero-Based Budgeting\n"
            "Every rupee of income is assigned a job so that income minus expenses equals zero. "
            "Start by listing total monthly income. Then list all expenses (fixed + variable) "
            "and savings goals. Adjust until the difference is Rs.0. "
            "This method works well for people with irregular income (freelancers, gig workers). "
            "Tools: spreadsheet or apps like Walnut, Money Manager."
        ),
        metadata={"category": "budgeting", "strategy": "zero_based"},
    ),
    Document(
        page_content=(
            "Budgeting Tip: Track Small Daily Expenses\n"
            "Small expenses like chai (Rs.20), auto rides (Rs.50), and impulse snacks add up quickly. "
            "Tracking 10 such items per day = Rs.500/day = Rs.15,000/month in untracked spending. "
            "Use UPI apps (PhonePe, GPay) transaction history for a complete daily log. "
            "Set a daily discretionary spending limit alert in your banking app."
        ),
        metadata={"category": "budgeting", "strategy": "daily_tracking"},
    ),

    # 14-17 · Fintech App Descriptions
    Document(
        page_content=(
            "App: CRED\n"
            "CRED is a members-only platform for high credit score individuals (750+). "
            "Features: pay credit card bills and earn CRED coins, get exclusive brand offers, "
            "rent payment via credit card, CRED Pay for merchant payments, CRED Stash (personal "
            "loan up to Rs.5 lakh), and CRED Travel for hotel/flight bookings. "
            "Best for: credit card users wanting rewards and bill management."
        ),
        metadata={"category": "fintech_apps", "app": "CRED"},
    ),
    Document(
        page_content=(
            "App: Groww\n"
            "Groww is a SEBI-registered investment platform. Users can invest in direct mutual "
            "funds (zero commission), stocks (NSE/BSE), US stocks, ETFs, FDs, and digital gold. "
            "Supports SIP starting at Rs.100/month. Offers a clean UI with portfolio tracking, "
            "personalized fund recommendations, and tax harvesting tools. "
            "Best for: beginner investors wanting an easy entry into the stock market."
        ),
        metadata={"category": "fintech_apps", "app": "Groww"},
    ),
    Document(
        page_content=(
            "App: Jar\n"
            "Jar automatically saves small amounts (round-ups on UPI transactions) and invests "
            "them in 24K digital gold. Example: you spend Rs.45 via UPI, Jar rounds up Rs.5 "
            "and saves it in gold. Users can also set daily savings targets (Rs.10-Rs.500/day). "
            "Gold can be redeemed as physical gold coins. "
            "Best for: people who struggle to save manually and want micro-savings."
        ),
        metadata={"category": "fintech_apps", "app": "Jar"},
    ),
    Document(
        page_content=(
            "Apps: Paytm and PhonePe\n"
            "Paytm: All-in-one super-app for UPI payments, mobile/DTH recharge, bill payment, "
            "Paytm Wallet, movie tickets, travel bookings, and Paytm Money (investments). "
            "PhonePe: India's largest UPI app by volume. Features UPI transfers, bill payments, "
            "insurance (2-wheeler, health), mutual funds, and PhonePe Switch (mini-apps for "
            "Swiggy, Ola, IRCTC, etc.). Both offer transaction history export useful for "
            "expense tracking."
        ),
        metadata={"category": "fintech_apps", "app": "Paytm_PhonePe"},
    ),

    # 18 · Overspend Alerts
    Document(
        page_content=(
            "Feature: Overspend Alerts\n"
            "Sahayak monitors cumulative spending per category each month. When spending in a "
            "category exceeds the pre-set limit (e.g., Food > Rs.8,000/month), an alert is "
            "triggered: 'You have spent Rs.8,500 on Food this month, exceeding your Rs.8,000 "
            "limit by Rs.500. Consider reducing dining-out frequency or choosing more affordable "
            "options.' Categories tracked: Food, Travel, Shopping, Entertainment, Utilities. "
            "Users can set custom limits or use AI-recommended limits based on income profile."
        ),
        metadata={"category": "features", "feature": "overspend_alerts"},
    ),

    # 19 · Recurring Bill Prediction
    Document(
        page_content=(
            "Feature: Recurring Bill Prediction\n"
            "Sahayak detects recurring payments by analysing SMS transaction history. "
            "If the same merchant (e.g., Netflix, Jio, gym) is charged every 28-31 days with "
            "a similar amount (+-10%), it is classified as a subscription. "
            "The system then predicts the next due date and amount: "
            "'Your Jio postpaid bill of Rs.799 is due on 05-Mar-2026. Ensure sufficient balance.' "
            "Categories: streaming (Netflix, Hotstar), telecom (Jio, Airtel), gym, insurance. "
            "Helps users avoid late fees and missed payment penalties."
        ),
        metadata={"category": "features", "feature": "recurring_bills"},
    ),

    # 20 · Sample Q&A Conversations
    Document(
        page_content=(
            "Sample Conversation: Expense Categorization and App Recommendations\n"
            "User: I spent Rs.500 at Starbucks today. What category is this?\n"
            "Sahayak: That expense at Starbucks falls under the 'Food & Dining' category. "
            "Starbucks is a cafe, so it's treated as a dining-out expense. You've now spent "
            "Rs.2,300 on Food & Dining this month. Your monthly limit is Rs.8,000, so you have "
            "Rs.5,700 remaining for the month.\n\n"
            "User: What apps can help me save money?\n"
            "Sahayak: Here are some great Indian savings apps: "
            "1) Jar - automatically saves round-ups from your UPI spends into digital gold. "
            "2) Groww - start a SIP mutual fund from as low as Rs.100/month. "
            "3) CRED - earn coins on credit card bill payments and get cashback offers. "
            "4) ET Money - tracks all your finances and suggests tax-saving investments."
        ),
        metadata={"category": "sample_conversations", "type": "qa"},
    ),
]


def main():
    print("Initializing Ollama embeddings (nomic-embed-text)...")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    print(f"Creating / loading ChromaDB at '{CHROMA_DIR}'...")
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )

    # Clear existing docs before re-inserting to avoid duplicates on re-run
    existing = vectorstore.get()
    if existing and existing.get("ids"):
        vectorstore.delete(ids=existing["ids"])
        print(f"Cleared {len(existing['ids'])} existing documents.")

    print(f"Adding {len(DOCUMENTS)} documents to ChromaDB...")
    vectorstore.add_documents(DOCUMENTS)

    print(f"ChromaDB populated with {len(DOCUMENTS)} documents.")
    print(f"Vector store saved at: {os.path.abspath(CHROMA_DIR)}")


if __name__ == "__main__":
    main()
