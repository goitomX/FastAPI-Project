from enum import Enum


class District(str, Enum):
    DISTRICT1 = "District1"
    DISTRICT2 = "District2"
    DISTRICT3 = "Arbaminch"
    DISTRICT4 = "Sodo"
    DISTRICT5 = "Hossana"
    DISTRICT6 = "Karate"
    DISTRICT7 = "Bonga"
    DISTRICT8 = "Jemu"
    DISTRICT9 = "Dilla"
    DISTRICT10 = "Masha"
    DISTRICT11 = "Bonga"
    District12 = "Tarcha"
    DISTRICT13 = "Mizan"
    DISTRICT14 = "Hawassa Sidama"
    DISTRICT15 = "Worabe"
    DISTRICT16 = "Sawla"
    DISTRICT17 = "Welkite"
    District18 = "Jinka"
    DISTRICT19 = "Hawassa Ketema"
    DISTRICT20 = "Durame"
    DISTRIct21 = "Halaba"

class ReportCategory(str, Enum):
    OPERATION = "Operation"
    FINANCE = "Finance"
    RISK = "Risk"
    HR = "HR"
    IT = "IT"

class ReportType(str, Enum):
    TRIAL_BALANCE = "Trial Balance OB_TB001"
    INCOME_STATEMENT = "Income Statement NBE_FIN006"
    BALANCE_SHEET = "Balance Sheet – Institutional	NBE_FIN004"
    BREAKDOWN_OF_INCOME_ACCOUNTS = "Breakdown of Income Accounts BRE_INC001"
    BREAKDOWN_OF__EXPENSES = "Breakdown of Expenses	BRE_EXP001"
    MONTHLY_AVERAGE_RESERVE_REPORT = "Monthly Average Reserve Report NP024"
    LIQUIDITY_REQUIREMENT_REPORT = "Liquidity Requirement Report	NBE_FIN003"
    PROFIT_AND_LOSS_STATEMENT = "Profit and Loss Statement NBE_FIN010"
    BALANCE_SHEET_NBE = "Balance Sheet – NBE NBE_FIN005"
    NON_PERFORMING_LOANS_AND_ADVANCES_AND_PROVISIONS = "Non-Performing Loans and Advances & Provisions	NBE_FIN008"
    LOAN_CLASSIFICATION_AND_PROVISIONING = "Loan Classification and Provisioning NBE_FIN007"
    FIXED_ASSET = "Fixed Asset / PPE OB_FIN003"
    CAPITAL_ADEQUACY_REPORT = "Capital Adequacy Report – On-Balance Sheet NBE_FIN011"
    CAPITAL_ADEQUACY_REPORT = "Capital Adequacy Report – Off-Balance Sheet	NBE_FIN012"
    CAPITAL_ADEQUACY_REPORT_QRTR = "Capital Adequacy Report (Quarterly) – Capital Components NBE_FIN013"
    MATURITY_OF_ASSETS_AND_LIABILITIES = "Maturity of Assets & Liabilities	NBE_FIN014"

    LOAN_AND_ADVANCE_DISBURSEMENT_COLLECTION_AND_OUTSTANDING = "Loan and Advance Disbursement, Collection and Outstanding NBE_LN001"
    LOAN_TO_RELATED_PARTIES = "Loan to Related Parties NBE_LN002"
    BORROWERS_EXCEED_10_PERCENT = "Borrowers Exceed 10 Percent NBE_LN003"
    PERSONAL_INFORMATION_INDIVIDUAL = "Personal Information Individual NBE_PIF001"
    INSURANCE_ACTIVITY_REPORT = "Insurance Activity Report OB_INSU01"
    ARRAERS_BY_AGE_INDIVIDUAL = "Arrears by Age Individual OB_ARR01"
    ARREARS_BENEFICIARY = "Arrears Beneficiary OB_ARR02"


# Parent-Child Mapping
CATEGORY_REPORT_MAPPING = {
    ReportCategory.FINANCE: [
        ReportType.TRIAL_BALANCE,
        ReportType.INCOME_STATEMENT,
        ReportType.BALANCE_SHEET,
        ReportType.BREAKDOWN_OF_INCOME_ACCOUNTS,  
        ReportType.BREAKDOWN_OF__EXPENSES,
        ReportType.MONTHLY_AVERAGE_RESERVE_REPORT,
        ReportType.LIQUIDITY_REQUIREMENT_REPORT,
        ReportType.PROFIT_AND_LOSS_STATEMENT,
        ReportType.BALANCE_SHEET_NBE,
        ReportType.NON_PERFORMING_LOANS_AND_ADVANCES_AND_PROVISIONS,
        ReportType.LOAN_CLASSIFICATION_AND_PROVISIONING,
        ReportType.FIXED_ASSET,
        ReportType.CAPITAL_ADEQUACY_REPORT,
        ReportType.CAPITAL_ADEQUACY_REPORT,
        ReportType.CAPITAL_ADEQUACY_REPORT_QRTR,
        ReportType.MATURITY_OF_ASSETS_AND_LIABILITIES  

    ],
    ReportCategory.OPERATION:
        [ReportType.LOAN_AND_ADVANCE_DISBURSEMENT_COLLECTION_AND_OUTSTANDING,
         ReportType.LOAN_TO_RELATED_PARTIES,
         ReportType.BORROWERS_EXCEED_10_PERCENT,
         ReportType.PERSONAL_INFORMATION_INDIVIDUAL,
         ReportType.INSURANCE_ACTIVITY_REPORT,
         ReportType.ARRAERS_BY_AGE_INDIVIDUAL,
         ReportType.ARREARS_BENEFICIARY
        
         ],
   
}