from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
)

class BillingAlarmStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, billing_email: str, monthly_budget: float, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # SNS Topic for billing alerts (in us-east-1)
        topic = sns.Topic(self, "BillingAlertsTopic", topic_name="billing-alerts")
        topic.add_subscription(subs.EmailSubscription(billing_email))

        # AWS/Billing metric only exists in us-east-1
        total_cost_metric = cloudwatch.Metric(
            namespace="AWS/Billing",
            metric_name="EstimatedCharges",
            dimensions_map={"Currency": "USD"},
            period=Duration.hours(6),
            statistic="Maximum",
        )

        # Alarm at 80% of the monthly budget
        alarm = cloudwatch.Alarm(
            self,
            "MonthlySpend80Pct",
            metric=total_cost_metric,
            threshold=monthly_budget * 0.8,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )
        alarm.add_alarm_action(cw_actions.SnsAction(topic))
