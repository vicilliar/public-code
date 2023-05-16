import stripe
import uuid
import os

stripe.api_key = os.environ['STRIPE_API_KEY']
STORAGE_SUBSCRIPTION_ITEM_ID = "si_NblS55RqpznKxi"
CPU_SUBSCRIPTION_ITEM_ID = "si_NblSxrmxGTJynn"
GPU_SUBSCRIPTION_ITEM_ID = "si_NblSsWQMzsefYe"

storage_hours = 3
inference_cpu_hours = 4
inference_gpu_hours = 5

# Add hours usage record for storage
if storage_hours:
    stripe.SubscriptionItem.create_usage_record(
        STORAGE_SUBSCRIPTION_ITEM_ID,
        quantity=round(storage_hours),
        # timestamp=int(now.timestamp()),
        action='set',                       # This will overwrite old usage data for the month 
        idempotency_key=str(uuid.uuid4())   # Random so there are no collisions
    )

# Add hours usage record for CPU
if inference_cpu_hours:
    stripe.SubscriptionItem.create_usage_record(
        CPU_SUBSCRIPTION_ITEM_ID,
        quantity=round(inference_cpu_hours),
        #timestamp=int(now.timestamp()),
        action='set',                       # This will overwrite old usage data for the month 
        idempotency_key=str(uuid.uuid4())   # Random so there are no collissions
    )

# Add hours usage record for GPU
if inference_gpu_hours:
    stripe.SubscriptionItem.create_usage_record(
        GPU_SUBSCRIPTION_ITEM_ID,
        quantity=round(inference_gpu_hours),
        #timestamp=int(now.timestamp()),
        action='set',                       # This will overwrite old usage data for the month 
        idempotency_key=str(uuid.uuid4())   # Random so there are no collissions
    )