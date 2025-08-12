"""
Legal Text Data Generator for Enhanced Phase 3 Pipeline
=====================================================

This module generates synthetic legal text data for training and evaluation
of the enhanced ML pipeline with proper risk classification.
"""

import pandas as pd
import numpy as np
import random
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import warnings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)
warnings.filterwarnings('ignore')

class LegalTextGenerator:
    """Generator for synthetic legal text data with risk classification."""
    
    def __init__(self, random_seed: int = 42):
        """
        Initialize the legal text generator.
        
        Args:
            random_seed: Random seed for reproducibility
        """
        self.random_seed = random_seed
        random.seed(random_seed)
        np.random.seed(random_seed)
        
        # Legal document templates by category and risk level
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize legal text templates."""
        return {
            'contracts': {
                'HighRisk': [
                    "This agreement contains clauses that may violate regulatory compliance standards. The parties acknowledge potential legal liabilities and regulatory risks associated with this contract. Failure to comply may result in significant penalties and legal action.",
                    "This contract includes high-risk provisions that could lead to substantial financial losses. The terms contain ambiguous language that may be interpreted unfavorably in court. Both parties assume significant legal and financial risks.",
                    "This agreement involves complex regulatory requirements with potential for non-compliance. The contract terms may conflict with existing laws and regulations. Legal counsel strongly advises against proceeding without modifications."
                ],
                'MediumRisk': [
                    "This contract contains standard terms and conditions with moderate legal implications. The parties should review all provisions carefully before execution. Some clauses may require legal interpretation.",
                    "This agreement includes typical business terms with standard risk allocation. The contract follows industry practices but may need customization for specific circumstances. Legal review is recommended.",
                    "This contract contains provisions that are generally acceptable but may require modification based on specific business needs. The terms are standard but should be reviewed for compliance."
                ],
                'LowRisk': [
                    "This agreement contains standard, low-risk terms and conditions. The contract follows established legal precedents and industry best practices. All provisions are clear and enforceable.",
                    "This contract includes straightforward terms with minimal legal complexity. The agreement is designed to be easily understood and implemented. Standard legal protections are included.",
                    "This agreement contains simple, clear terms with low legal risk. The contract is designed for routine business transactions with standard protections and obligations."
                ]
            },
            'compliance': {
                'HighRisk': [
                    "This compliance document addresses critical regulatory requirements with significant enforcement risks. Failure to comply may result in severe penalties, including criminal charges. Immediate action is required to address identified violations.",
                    "This compliance framework contains high-risk areas requiring immediate attention. The organization faces potential regulatory sanctions and legal action. Comprehensive remediation is necessary.",
                    "This compliance assessment reveals significant regulatory violations with potential for severe consequences. The organization must implement immediate corrective actions to avoid legal penalties."
                ],
                'MediumRisk': [
                    "This compliance document outlines standard regulatory requirements with moderate enforcement risks. The organization should address identified issues to maintain compliance status. Regular monitoring is recommended.",
                    "This compliance framework contains areas requiring attention but with manageable risks. The organization should implement recommended improvements to enhance compliance posture.",
                    "This compliance assessment identifies areas for improvement with moderate regulatory implications. The organization should develop action plans to address identified gaps."
                ],
                'LowRisk': [
                    "This compliance document demonstrates strong adherence to regulatory requirements. The organization maintains excellent compliance posture with minimal enforcement risks. Regular monitoring continues.",
                    "This compliance framework shows consistent adherence to regulatory standards. The organization demonstrates good compliance practices with low risk of regulatory action.",
                    "This compliance assessment indicates strong regulatory compliance with minimal areas for improvement. The organization maintains effective compliance controls and monitoring."
                ]
            },
            'litigation': {
                'HighRisk': [
                    "This litigation matter involves complex legal issues with significant financial and reputational risks. The case presents substantial legal challenges requiring expert legal representation. Settlement negotiations may be advisable.",
                    "This legal proceeding involves high-stakes litigation with potential for substantial damages. The case requires extensive legal resources and expert testimony. The outcome may significantly impact the organization.",
                    "This litigation matter presents significant legal and financial risks requiring immediate attention. The case involves complex legal issues with potential for adverse outcomes. Strategic legal planning is essential."
                ],
                'MediumRisk': [
                    "This litigation matter involves standard legal issues with moderate complexity. The case requires appropriate legal representation and strategic planning. The outcome may have moderate financial impact.",
                    "This legal proceeding involves typical litigation risks with manageable complexity. The case requires standard legal resources and may be resolved through negotiation or mediation.",
                    "This litigation matter presents moderate legal risks requiring appropriate legal attention. The case involves standard legal issues with potential for resolution through standard legal processes."
                ],
                'LowRisk': [
                    "This litigation matter involves straightforward legal issues with minimal complexity. The case can be managed with standard legal resources and procedures. The outcome is likely to be favorable.",
                    "This legal proceeding involves routine legal matters with low risk and complexity. The case can be resolved through standard legal processes with minimal resource requirements.",
                    "This litigation matter presents low legal risks with straightforward resolution options. The case involves simple legal issues that can be addressed through standard legal procedures."
                ]
            },
            'regulatory': {
                'HighRisk': [
                    "This regulatory matter involves significant compliance violations with potential for severe penalties. The organization faces immediate regulatory action and must implement comprehensive corrective measures. Legal counsel is essential.",
                    "This regulatory issue presents critical compliance challenges requiring immediate attention. The organization may face regulatory sanctions and must develop comprehensive remediation plans.",
                    "This regulatory matter involves serious violations requiring immediate corrective action. The organization faces potential regulatory enforcement and must implement robust compliance measures."
                ],
                'MediumRisk': [
                    "This regulatory matter involves moderate compliance issues requiring attention. The organization should address identified concerns to maintain regulatory compliance. Regular monitoring is recommended.",
                    "This regulatory issue presents manageable compliance challenges requiring appropriate attention. The organization should implement recommended improvements to enhance regulatory compliance.",
                    "This regulatory matter involves standard compliance issues with moderate implications. The organization should address identified areas to maintain good regulatory standing."
                ],
                'LowRisk': [
                    "This regulatory matter involves routine compliance requirements with minimal risk. The organization maintains good regulatory standing with standard compliance measures. Regular monitoring continues.",
                    "This regulatory issue presents low-risk compliance matters requiring standard attention. The organization demonstrates good regulatory practices with minimal compliance concerns.",
                    "This regulatory matter involves straightforward compliance requirements with low risk. The organization maintains effective regulatory compliance with standard monitoring procedures."
                ]
            }
        }
    
    def generate_text(self, category: str, risk_level: str, 
                     template_variation: bool = True) -> str:
        """
        Generate legal text based on category and risk level.
        
        Args:
            category: Legal document category
            risk_level: Risk level (HighRisk, MediumRisk, LowRisk)
            template_variation: Whether to add variations to templates
            
        Returns:
            str: Generated legal text
        """
        if category not in self.templates or risk_level not in self.templates[category]:
            raise ValueError(f"Invalid category '{category}' or risk_level '{risk_level}'")
        
        # Select base template
        templates = self.templates[category][risk_level]
        base_text = random.choice(templates)
        
        if template_variation:
            # Add variations to make text more diverse
            variations = [
                "The parties acknowledge the importance of legal compliance.",
                "This document should be reviewed by qualified legal counsel.",
                "All terms and conditions are subject to applicable laws.",
                "The organization maintains appropriate legal safeguards.",
                "Regular legal review is recommended for ongoing compliance.",
                "This agreement is governed by applicable legal standards.",
                "The parties agree to resolve disputes through appropriate legal channels.",
                "Legal documentation should be maintained for audit purposes.",
                "The organization follows established legal procedures.",
                "Compliance with regulatory requirements is essential."
            ]
            
            # Add 1-3 random variations
            num_variations = random.randint(1, 3)
            selected_variations = random.sample(variations, num_variations)
            
            # Combine base text with variations
            full_text = base_text + " " + " ".join(selected_variations)
        else:
            full_text = base_text
        
        return full_text
    
    def generate_dataset(self, 
                        total_samples: int = 1200,
                        category_distribution: Optional[Dict[str, float]] = None,
                        risk_distribution: Optional[Dict[str, float]] = None) -> pd.DataFrame:
        """
        Generate a complete dataset with specified distribution.
        
        Args:
            total_samples: Total number of samples to generate
            category_distribution: Distribution of legal categories
            risk_distribution: Distribution of risk levels
            
        Returns:
            pd.DataFrame: Generated dataset with text and labels
        """
        if category_distribution is None:
            category_distribution = {
                'contracts': 0.3,
                'compliance': 0.25,
                'litigation': 0.25,
                'regulatory': 0.2
            }
        
        if risk_distribution is None:
            risk_distribution = {
                'HighRisk': 0.33,
                'MediumRisk': 0.34,
                'LowRisk': 0.33
            }
        
        # Calculate samples per category and risk level
        samples_per_category = {}
        remaining_samples = total_samples
        
        for category, proportion in category_distribution.items():
            if category == list(category_distribution.keys())[-1]:
                # Last category gets remaining samples
                samples_per_category[category] = remaining_samples
            else:
                samples = int(total_samples * proportion)
                samples_per_category[category] = samples
                remaining_samples -= samples
        
        # Generate data
        data = []
        categories = list(self.templates.keys())
        risk_levels = ['HighRisk', 'MediumRisk', 'LowRisk']
        
        for category in categories:
            category_samples = samples_per_category.get(category, 0)
            if category_samples == 0:
                continue
            
            # Distribute samples across risk levels
            remaining_risk_samples = category_samples
            
            for i, risk_level in enumerate(risk_levels):
                if i == len(risk_levels) - 1:
                    # Last risk level gets remaining samples
                    risk_samples = remaining_risk_samples
                else:
                    risk_proportion = risk_distribution.get(risk_level, 1/3)
                    risk_samples = int(category_samples * risk_proportion)
                    remaining_risk_samples -= risk_samples
                
                for _ in range(risk_samples):
                    text = self.generate_text(category, risk_level)
                    data.append({
                        'text': text,
                        'label': risk_level,
                        'category': category
                    })
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Shuffle the data
        df = df.sample(frac=1, random_state=self.random_seed).reset_index(drop=True)
        
        return df
    
    def create_train_valid_test_splits(self, 
                                      df: pd.DataFrame,
                                      train_size: int = 840,
                                      valid_size: int = 180,
                                      test_size: int = 180) -> Dict[str, pd.DataFrame]:
        """
        Create train, validation, and test splits.
        
        Args:
            df: Input DataFrame
            train_size: Number of training samples
            valid_size: Number of validation samples
            test_size: Number of test samples
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing train, valid, and test splits
        """
        # Ensure we have enough data
        total_required = train_size + valid_size + test_size
        if len(df) < total_required:
            raise ValueError(f"Insufficient data: {len(df)} samples, need {total_required}")
        
        # Create splits
        train_df = df.head(train_size)
        valid_df = df.iloc[train_size:train_size + valid_size]
        test_df = df.iloc[train_size + valid_size:train_size + valid_size + test_size]
        
        return {
            'train': train_df,
            'valid': valid_df,
            'test': test_df
        }
    
    def save_splits(self, splits: Dict[str, pd.DataFrame], 
                   output_dir: str = "data/text_corpus") -> None:
        """
        Save train, validation, and test splits to CSV files.
        
        Args:
            splits: Dictionary containing train, valid, and test DataFrames
            output_dir: Output directory for saving files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for split_name, df in splits.items():
            file_path = output_path / f"{split_name}.csv"
            df.to_csv(file_path, index=False)
            logger.info(r"Saved {split_name} split: {len(df)} samples -> {file_path}")
    
    def generate_and_save_dataset(self,
                                 total_samples: int = 1200,
                                 train_size: int = 840,
                                 valid_size: int = 180,
                                 test_size: int = 180,
                                 output_dir: str = "data/text_corpus",
                                 category_distribution: Optional[Dict[str, float]] = None,
                                 risk_distribution: Optional[Dict[str, float]] = None) -> Dict[str, pd.DataFrame]:
        """
        Generate and save complete dataset with splits.
        
        Args:
            total_samples: Total number of samples to generate
            train_size: Number of training samples
            valid_size: Number of validation samples
            test_size: Number of test samples
            output_dir: Output directory for saving files
            category_distribution: Distribution of legal categories
            risk_distribution: Distribution of risk levels
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing train, valid, and test splits
        """
        logger.info(r"Generating {total_samples} legal text samples...")
        
        # Generate dataset
        df = self.generate_dataset(
            total_samples=total_samples,
            category_distribution=category_distribution,
            risk_distribution=risk_distribution
        )
        
        # Create splits
        splits = self.create_train_valid_test_splits(
            df, train_size, valid_size, test_size
        )
        
        # Save splits
        self.save_splits(splits, output_dir)
        
        # Print summary
        logger.info(r"\nDataset Summary:")
        logger.info(r"Total samples: {len(df)}")
        logger.info(r"Categories: {df['category'].value_counts().to_dict()}")
        logger.info(r"Risk levels: {df['label'].value_counts().to_dict()}")
        
        return splits

def create_legal_text_generator(random_seed: int = 42) -> LegalTextGenerator:
    """
    Factory function to create legal text generator.
    
    Args:
        random_seed: Random seed for reproducibility
        
    Returns:
        LegalTextGenerator: Configured legal text generator instance
    """
    return LegalTextGenerator(random_seed=random_seed)

def generate_enhanced_dataset(output_dir: str = "data/text_corpus",
                             total_samples: int = 1200,
                             random_seed: int = 42) -> Dict[str, pd.DataFrame]:
    """
    Generate enhanced legal text dataset with proper splits.
    
    Args:
        output_dir: Output directory for saving files
        total_samples: Total number of samples to generate
        random_seed: Random seed for reproducibility
        
    Returns:
        Dict[str, pd.DataFrame]: Dictionary containing train, valid, and test splits
    """
    generator = create_legal_text_generator(random_seed=random_seed)
    
    # Calculate split sizes (70% train, 15% valid, 15% test)
    train_size = int(total_samples * 0.7)
    valid_size = int(total_samples * 0.15)
    test_size = total_samples - train_size - valid_size
    
    return generator.generate_and_save_dataset(
        total_samples=total_samples,
        train_size=train_size,
        valid_size=valid_size,
        test_size=test_size,
        output_dir=output_dir
    )

if __name__ == "__main__":
    # Example usage
    splits = generate_enhanced_dataset()
    logger.info(r"Dataset generation completed successfully!")
