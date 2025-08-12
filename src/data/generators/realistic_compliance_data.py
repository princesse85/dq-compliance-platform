"""
Realistic Compliance Data Generator

This module generates hyper-realistic compliance and legal documents
using Faker to create a comprehensive dataset for the ML models.
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
from typing import List, Dict
import json

# Initialize Faker with multiple locales for realistic data
fake = Faker(['en_US', 'en_GB', 'en_CA'])

# Set seed for reproducibility
Faker.seed(42)
np.random.seed(42)
random.seed(42)

class ComplianceDataGenerator:
    """Generates realistic compliance and legal documents."""
    
    def __init__(self):
        self.companies = [fake.company() for _ in range(50)]
        self.regulatory_bodies = [
            "SEC", "FINRA", "CFTC", "OCC", "FDIC", "CFPB", "FTC", "EPA", "FDA", "OSHA",
            "GDPR", "CCPA", "SOX", "GLBA", "HIPAA", "PCI DSS", "ISO 27001", "NIST"
        ]
        self.risk_keywords = {
            "high": ["critical", "severe", "immediate", "urgent", "enforcement", "penalty", "violation", "breach"],
            "medium": ["moderate", "attention", "review", "concern", "potential", "risk", "compliance"],
            "low": ["standard", "routine", "normal", "acceptable", "compliant", "effective", "successful"]
        }
        
    def generate_contract_text(self, risk_level: str) -> str:
        """Generate realistic contract text based on risk level."""
        company_a = random.choice(self.companies)
        company_b = random.choice(self.companies)
        
        if risk_level == "HighRisk":
            template = f"""
This agreement between {company_a} and {company_b} involves complex regulatory requirements with potential for non-compliance. 
The contract terms may conflict with existing laws and regulations, particularly regarding {random.choice(['data privacy', 'financial reporting', 'environmental compliance', 'labor standards'])}. 
Legal counsel strongly advises against proceeding without modifications due to {random.choice(['ambiguous language', 'regulatory conflicts', 'enforcement risks', 'liability exposure'])}. 
The parties acknowledge potential legal liabilities and regulatory risks associated with this contract. 
Failure to comply may result in significant penalties and legal action. 
This document should be reviewed by qualified legal counsel before execution.
            """
        elif risk_level == "MediumRisk":
            template = f"""
This agreement between {company_a} and {company_b} contains standard terms and conditions with moderate legal implications. 
The parties should review all provisions carefully before execution. Some clauses may require legal interpretation, 
particularly regarding {random.choice(['intellectual property', 'confidentiality', 'termination', 'dispute resolution'])}. 
The contract follows industry practices but may need customization for specific circumstances. 
Legal review is recommended to ensure compliance with applicable regulations.
            """
        else:  # LowRisk
            template = f"""
This agreement between {company_a} and {company_b} contains simple, clear terms with low legal risk. 
The contract is designed for routine business transactions with standard protections and obligations. 
All provisions are clear and enforceable, following established legal precedents and industry best practices. 
The agreement demonstrates good compliance practices with minimal regulatory concerns.
            """
        
        return template.strip()
    
    def generate_litigation_text(self, risk_level: str) -> str:
        """Generate realistic litigation text based on risk level."""
        company = random.choice(self.companies)
        
        if risk_level == "HighRisk":
            template = f"""
This litigation matter involving {company} presents significant legal and financial risks requiring immediate attention. 
The case involves complex legal issues with potential for adverse outcomes, including {random.choice(['substantial damages', 'regulatory enforcement', 'criminal charges', 'class action'])}. 
Strategic legal planning is essential due to {random.choice(['multiple jurisdictions', 'complex evidence', 'expert testimony requirements', 'regulatory overlap'])}. 
The outcome may significantly impact the organization's financial position and reputation.
            """
        elif risk_level == "MediumRisk":
            template = f"""
This litigation matter involving {company} involves standard legal issues with moderate complexity. 
The case requires appropriate legal representation and strategic planning. The outcome may have moderate financial impact. 
The case involves {random.choice(['contract disputes', 'employment matters', 'regulatory compliance', 'intellectual property'])} 
and may be resolved through negotiation or mediation.
            """
        else:  # LowRisk
            template = f"""
This litigation matter involving {company} involves straightforward legal issues with minimal complexity. 
The case can be managed with standard legal resources and procedures. The outcome is likely to be favorable. 
The case involves routine {random.choice(['contract interpretation', 'regulatory compliance', 'employment matters', 'commercial disputes'])} 
and can be resolved through standard legal processes.
            """
        
        return template.strip()
    
    def generate_regulatory_text(self, risk_level: str) -> str:
        """Generate realistic regulatory compliance text based on risk level."""
        company = random.choice(self.companies)
        regulatory_body = random.choice(self.regulatory_bodies)
        
        if risk_level == "HighRisk":
            template = f"""
This regulatory matter involving {company} involves significant compliance violations with potential for severe penalties. 
The organization faces immediate regulatory action from {regulatory_body} and must implement comprehensive corrective measures. 
The violations include {random.choice(['data breaches', 'financial misreporting', 'environmental violations', 'safety violations'])} 
that may result in {random.choice(['criminal charges', 'substantial fines', 'license revocation', 'enforcement actions'])}. 
Legal counsel is essential for navigating the regulatory enforcement process.
            """
        elif risk_level == "MediumRisk":
            template = f"""
This regulatory matter involving {company} involves moderate compliance issues requiring attention. 
The organization should address identified concerns to maintain regulatory compliance with {regulatory_body}. 
The issues include {random.choice(['reporting delays', 'procedural deficiencies', 'documentation gaps', 'training requirements'])} 
that require corrective action within specified timeframes.
            """
        else:  # LowRisk
            template = f"""
This regulatory matter involving {company} involves routine compliance requirements with minimal risk. 
The organization maintains effective regulatory compliance with {regulatory_body} through standard monitoring procedures. 
All compliance activities are current and meet regulatory expectations. Regular monitoring continues to ensure ongoing compliance.
            """
        
        return template.strip()
    
    def generate_compliance_text(self, risk_level: str) -> str:
        """Generate realistic compliance assessment text based on risk level."""
        company = random.choice(self.companies)
        
        if risk_level == "HighRisk":
            template = f"""
This compliance assessment for {company} reveals significant regulatory violations with potential for severe consequences. 
The organization must implement immediate corrective actions to avoid legal penalties and regulatory enforcement. 
Critical compliance gaps identified include {random.choice(['data protection', 'financial controls', 'environmental compliance', 'safety protocols'])}. 
Failure to address these issues may result in {random.choice(['regulatory sanctions', 'criminal charges', 'substantial fines', 'operational restrictions'])}.
            """
        elif risk_level == "MediumRisk":
            template = f"""
This compliance assessment for {company} identifies areas for improvement with moderate regulatory implications. 
The organization should develop action plans to address identified gaps in {random.choice(['process controls', 'documentation', 'training programs', 'monitoring systems'])}. 
While no immediate enforcement action is anticipated, timely remediation is recommended to maintain good regulatory standing.
            """
        else:  # LowRisk
            template = f"""
This compliance assessment for {company} indicates strong regulatory compliance with minimal areas for improvement. 
The organization maintains effective compliance controls and monitoring across all regulatory requirements. 
All compliance activities are current and meet or exceed regulatory expectations. 
The organization demonstrates good compliance practices with low risk of regulatory action.
            """
        
        return template.strip()
    
    def generate_dataset(self, num_samples: int = 5000) -> pd.DataFrame:
        """Generate a comprehensive dataset with realistic compliance documents."""
        print(f"Generating {num_samples} realistic compliance documents...")
        
        data = []
        categories = ["contracts", "litigation", "regulatory", "compliance"]
        risk_levels = ["LowRisk", "MediumRisk", "HighRisk"]
        
        # Create balanced dataset
        samples_per_category = num_samples // len(categories)
        samples_per_risk = samples_per_category // len(risk_levels)
        
        for category in categories:
            for risk_level in risk_levels:
                for _ in range(samples_per_risk):
                    if category == "contracts":
                        text = self.generate_contract_text(risk_level)
                    elif category == "litigation":
                        text = self.generate_litigation_text(risk_level)
                    elif category == "regulatory":
                        text = self.generate_regulatory_text(risk_level)
                    else:  # compliance
                        text = self.generate_compliance_text(risk_level)
                    
                    data.append({
                        "text": text,
                        "label": risk_level,
                        "category": category,
                        "company": random.choice(self.companies),
                        "date": fake.date_between(start_date='-2y', end_date='today'),
                        "document_id": fake.uuid4(),
                        "risk_score": self._get_risk_score(risk_level),
                        "compliance_score": self._get_compliance_score(risk_level)
                    })
        
        # Add some variation to make it more realistic
        extra_samples = num_samples - len(data)
        for _ in range(extra_samples):
            category = random.choice(categories)
            risk_level = random.choice(risk_levels)
            
            if category == "contracts":
                text = self.generate_contract_text(risk_level)
            elif category == "litigation":
                text = self.generate_litigation_text(risk_level)
            elif category == "regulatory":
                text = self.generate_regulatory_text(risk_level)
            else:
                text = self.generate_compliance_text(risk_level)
            
            data.append({
                "text": text,
                "label": risk_level,
                "category": category,
                "company": random.choice(self.companies),
                "date": fake.date_between(start_date='-2y', end_date='today'),
                "document_id": fake.uuid4(),
                "risk_score": self._get_risk_score(risk_level),
                "compliance_score": self._get_compliance_score(risk_level)
            })
        
        df = pd.DataFrame(data)
        
        # Shuffle the dataset
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        print(f"Generated {len(df)} documents")
        print(f"Category distribution:\n{df['category'].value_counts()}")
        print(f"Risk level distribution:\n{df['label'].value_counts()}")
        
        return df
    
    def _get_risk_score(self, risk_level: str) -> float:
        """Get numeric risk score based on risk level."""
        if risk_level == "HighRisk":
            return np.random.uniform(75, 95)
        elif risk_level == "MediumRisk":
            return np.random.uniform(45, 75)
        else:
            return np.random.uniform(20, 45)
    
    def _get_compliance_score(self, risk_level: str) -> float:
        """Get compliance score (inverse of risk)."""
        risk_score = self._get_risk_score(risk_level)
        return max(0, 100 - risk_score)

def create_realistic_datasets():
    """Create realistic training, validation, and test datasets."""
    generator = ComplianceDataGenerator()
    
    # Generate comprehensive dataset - INCREASED TO 25,000 SAMPLES
    full_dataset = generator.generate_dataset(num_samples=25000)
    
    # Split into train/validation/test (70/15/15)
    train_size = int(0.7 * len(full_dataset))
    val_size = int(0.15 * len(full_dataset))
    
    train_df = full_dataset[:train_size]
    val_df = full_dataset[train_size:train_size + val_size]
    test_df = full_dataset[train_size + val_size:]
    
    # Save datasets
    output_dir = "src/data/text_corpus"
    train_df.to_csv(f"{output_dir}/train.csv", index=False)
    val_df.to_csv(f"{output_dir}/valid.csv", index=False)
    test_df.to_csv(f"{output_dir}/test.csv", index=False)
    
    # Save metadata
    metadata = {
        "total_samples": len(full_dataset),
        "train_samples": len(train_df),
        "validation_samples": len(val_df),
        "test_samples": len(test_df),
        "categories": full_dataset['category'].unique().tolist(),
        "risk_levels": full_dataset['label'].unique().tolist(),
        "generated_date": datetime.now().isoformat(),
        "data_generator": "ComplianceDataGenerator with Faker (Enhanced)"
    }
    
    with open(f"{output_dir}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✅ Enhanced Datasets created successfully!")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Train: {len(train_df)} samples")
    print(f"📊 Validation: {len(val_df)} samples")
    print(f"📊 Test: {len(test_df)} samples")
    print(f"📄 Metadata saved to: {output_dir}/metadata.json")
    
    # Print detailed statistics
    print(f"\n📈 Dataset Statistics:")
    print(f"   Total documents: {len(full_dataset):,}")
    print(f"   Training samples: {len(train_df):,}")
    print(f"   Validation samples: {len(val_df):,}")
    print(f"   Test samples: {len(test_df):,}")
    print(f"   Categories: {len(full_dataset['category'].unique())}")
    print(f"   Risk levels: {len(full_dataset['label'].unique())}")
    print(f"   Average text length: {full_dataset['text'].str.len().mean():.0f} characters")

if __name__ == "__main__":
    create_realistic_datasets()
