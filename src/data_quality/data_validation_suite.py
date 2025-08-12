import great_expectations as ge
from great_expectations.core.expectation_suite import ExpectationSuite

def build_suite():
    suite = ExpectationSuite(expectation_suite_name="contract_register_suite")
    # Required columns
    required = ["contract_id","party_a","party_b","effective_date","governing_law","status"]
    # GE (v0.18) programmatic API using BatchRequest is heavy; use simple Dataset for pandas
    return suite, required

# Convenience checker (used by run_quality_checks)
REQUIRED_COLS = ["contract_id","party_a","party_b","effective_date","governing_law","status"]
VALID_CCY = {"GBP","EUR","USD","NGN","ZAR","INR"}
