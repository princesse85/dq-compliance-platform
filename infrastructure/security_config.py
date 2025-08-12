"""
Security configuration for the Enterprise Data Quality & Compliance Platform.

This module provides comprehensive security settings including encryption,
authentication, authorization, and compliance configurations.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    
    # Encryption Settings
    ENCRYPTION_ALGORITHM: str = "AES256"
    KMS_KEY_ALIAS: str = "enterprise-production-key"
    ENCRYPTION_CONTEXT: Dict[str, str] = None
    
    # Authentication Settings
    AUTH_PROVIDER: str = "cognito"  # cognito, okta, azure_ad
    AUTH_REGION: str = "eu-west-2"
    AUTH_USER_POOL_ID: str = ""
    AUTH_CLIENT_ID: str = ""
    AUTH_CLIENT_SECRET: str = ""
    
    # Authorization Settings
    ROLE_BASED_ACCESS_CONTROL: bool = True
    ADMIN_ROLES: List[str] = None
    USER_ROLES: List[str] = None
    READ_ONLY_ROLES: List[str] = None
    
    # Network Security
    VPC_ID: str = ""
    SUBNET_IDS: List[str] = None
    SECURITY_GROUP_IDS: List[str] = None
    ALLOWED_IP_RANGES: List[str] = None
    
    # API Security
    API_RATE_LIMIT: int = 1000
    API_BURST_LIMIT: int = 500
    API_KEY_REQUIRED: bool = True
    CORS_ALLOWED_ORIGINS: List[str] = None
    
    # Data Security
    DATA_CLASSIFICATION: Dict[str, str] = None
    PII_DETECTION_ENABLED: bool = True
    DATA_MASKING_ENABLED: bool = True
    DATA_RETENTION_DAYS: int = 2555  # 7 years
    
    # Audit and Compliance
    AUDIT_LOGGING_ENABLED: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 3650  # 10 years
    COMPLIANCE_FRAMEWORKS: List[str] = None
    
    # Monitoring and Alerting
    SECURITY_ALERTS_ENABLED: bool = True
    ALERT_EMAILS: List[str] = None
    ALERT_SLACK_CHANNEL: str = ""
    
    def __post_init__(self):
        """Initialize default values."""
        if self.ENCRYPTION_CONTEXT is None:
            self.ENCRYPTION_CONTEXT = {
                "environment": "production",
                "application": "enterprise-dq"
            }
        
        if self.ADMIN_ROLES is None:
            self.ADMIN_ROLES = ["admin", "super_admin"]
        
        if self.USER_ROLES is None:
            self.USER_ROLES = ["user", "analyst", "data_scientist"]
        
        if self.READ_ONLY_ROLES is None:
            self.READ_ONLY_ROLES = ["viewer", "auditor"]
        
        if self.SUBNET_IDS is None:
            self.SUBNET_IDS = []
        
        if self.SECURITY_GROUP_IDS is None:
            self.SECURITY_GROUP_IDS = []
        
        if self.ALLOWED_IP_RANGES is None:
            self.ALLOWED_IP_RANGES = []
        
        if self.CORS_ALLOWED_ORIGINS is None:
            self.CORS_ALLOWED_ORIGINS = []
        
        if self.DATA_CLASSIFICATION is None:
            self.DATA_CLASSIFICATION = {
                "public": "PUBLIC",
                "internal": "INTERNAL",
                "confidential": "CONFIDENTIAL",
                "restricted": "RESTRICTED"
            }
        
        if self.COMPLIANCE_FRAMEWORKS is None:
            self.COMPLIANCE_FRAMEWORKS = ["GDPR", "SOX", "HIPAA", "PCI-DSS"]
        
        if self.ALERT_EMAILS is None:
            self.ALERT_EMAILS = ["security@company.com"]
    
    def create_vpc_config(self) -> Dict[str, str]:
        """Create VPC configuration."""
        return {
            "cidr": "10.0.0.0/16",
            "enable_dns_hostnames": True,
            "enable_dns_support": True
        }
    
    def create_iam_policies(self) -> Dict[str, Dict]:
        """Create IAM policies for different roles."""
        return {
            "admin_policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "*",
                        "Resource": "*"
                    }
                ]
            },
            "user_policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject",
                            "lambda:InvokeFunction"
                        ],
                        "Resource": "*"
                    }
                ]
            }
        }
    
    def create_security_groups(self) -> Dict[str, List[Dict]]:
        """Create security group configurations."""
        return {
            "web_tier": [
                {
                    "protocol": "tcp",
                    "port": 80,
                    "source": "0.0.0.0/0"
                },
                {
                    "protocol": "tcp",
                    "port": 443,
                    "source": "0.0.0.0/0"
                }
            ],
            "app_tier": [
                {
                    "protocol": "tcp",
                    "port": 8080,
                    "source": "10.0.0.0/16"
                }
            ]
        }
    
    def is_valid_cidr(self, cidr: str) -> bool:
        """Validate CIDR notation."""
        import ipaddress
        try:
            ipaddress.IPv4Network(cidr, strict=False)
            return True
        except (ipaddress.AddressValueError, ValueError):
            return False
    
    def is_valid_port(self, port: int) -> bool:
        """Validate port number."""
        return 1 <= port <= 65535


class SecurityManager:
    """Security management utilities."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
    
    def validate_encryption_settings(self) -> bool:
        """Validate encryption configuration."""
        required_fields = [
            "ENCRYPTION_ALGORITHM",
            "KMS_KEY_ALIAS"
        ]
        
        for field in required_fields:
            if not getattr(self.config, field):
                raise ValueError(f"Missing required encryption field: {field}")
        
        return True
    
    def validate_authentication_settings(self) -> bool:
        """Validate authentication configuration."""
        if self.config.AUTH_PROVIDER == "cognito":
            required_fields = [
                "AUTH_USER_POOL_ID",
                "AUTH_CLIENT_ID"
            ]
            
            for field in required_fields:
                if not getattr(self.config, field):
                    raise ValueError(f"Missing required auth field: {field}")
        
        return True
    
    def validate_network_settings(self) -> bool:
        """Validate network security configuration."""
        if self.config.VPC_ID and not self.config.SUBNET_IDS:
            raise ValueError("VPC ID specified but no subnet IDs provided")
        
        return True
    
    def get_data_classification_level(self, data_type: str) -> str:
        """Get data classification level for data type."""
        return self.config.DATA_CLASSIFICATION.get(data_type, "INTERNAL")
    
    def is_authorized(self, user_role: str, required_role: str) -> bool:
        """Check if user has required role."""
        role_hierarchy = {
            "super_admin": ["super_admin", "admin", "user", "viewer"],
            "admin": ["admin", "user", "viewer"],
            "user": ["user", "viewer"],
            "viewer": ["viewer"]
        }
        
        return required_role in role_hierarchy.get(user_role, [])
    
    def should_mask_data(self, data_classification: str) -> bool:
        """Determine if data should be masked based on classification."""
        sensitive_levels = ["CONFIDENTIAL", "RESTRICTED"]
        return data_classification in sensitive_levels and self.config.DATA_MASKING_ENABLED
    
    def get_audit_config(self) -> Dict:
        """Get audit configuration."""
        return {
            "enabled": self.config.AUDIT_LOGGING_ENABLED,
            "retention_days": self.config.AUDIT_LOG_RETENTION_DAYS,
            "frameworks": self.config.COMPLIANCE_FRAMEWORKS
        }


class ComplianceManager:
    """Compliance management utilities."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
    
    def get_gdpr_requirements(self) -> Dict:
        """Get GDPR compliance requirements."""
        return {
            "data_minimization": True,
            "purpose_limitation": True,
            "storage_limitation": True,
            "accuracy": True,
            "integrity_confidentiality": True,
            "accountability": True,
            "right_to_access": True,
            "right_to_erasure": True,
            "data_portability": True
        }
    
    def get_sox_requirements(self) -> Dict:
        """Get SOX compliance requirements."""
        return {
            "audit_trail": True,
            "access_controls": True,
            "data_integrity": True,
            "change_management": True,
            "backup_recovery": True,
            "security_monitoring": True
        }
    
    def get_hipaa_requirements(self) -> Dict:
        """Get HIPAA compliance requirements."""
        return {
            "privacy_rule": True,
            "security_rule": True,
            "breach_notification": True,
            "administrative_safeguards": True,
            "physical_safeguards": True,
            "technical_safeguards": True
        }
    
    def validate_compliance(self, framework: str) -> Dict:
        """Validate compliance for specific framework."""
        validators = {
            "GDPR": self.get_gdpr_requirements,
            "SOX": self.get_sox_requirements,
            "HIPAA": self.get_hipaa_requirements
        }
        
        if framework not in validators:
            raise ValueError(f"Unsupported compliance framework: {framework}")
        
        return validators[framework]()


# Default security configuration
default_security_config = SecurityConfig()

# Security manager instance
security_manager = SecurityManager(default_security_config)

# Compliance manager instance
compliance_manager = ComplianceManager(default_security_config)
