"""Budget kill switch — turn a Cloud Billing budget alert into an actual cap.

A GCP budget only NOTIFIES; it never stops spend. This function subscribes to the
budget's Pub/Sub topic and detaches billing from the project once actual spend
reaches the budget amount, which does stop it.

Deploy: see README.md beside this file.

Env:
  KILL_PROJECT_ID   project to detach billing from when the threshold is crossed
  DRY_RUN           "1" to log the decision without detaching (default "0")

Note this is destructive by design: detaching billing stops every billable
resource in the target project, which is the point. Point KILL_PROJECT_ID at a
disposable project, never at one running anything you need.
"""
import base64
import json
import os

import functions_framework
from googleapiclient import discovery

KILL_PROJECT_ID = os.environ.get("KILL_PROJECT_ID", "")
DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"


def _billing():
    return discovery.build("cloudbilling", "v1", cache_discovery=False)


def _is_billing_enabled(project_name):
    res = _billing().projects().getBillingInfo(name=project_name).execute()
    return res.get("billingEnabled", False)


def _disable_billing(project_name):
    # Assigning an empty billingAccountName is what detaches billing.
    return _billing().projects().updateBillingInfo(
        name=project_name, body={"billingAccountName": ""}).execute()


@functions_framework.cloud_event
def stop_billing(cloud_event):
    if not KILL_PROJECT_ID:
        print("ERROR: KILL_PROJECT_ID is unset — refusing to act")
        return

    payload = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode())
    cost = float(payload.get("costAmount", 0))
    budget = float(payload.get("budgetAmount", 0))
    name = payload.get("budgetDisplayName", "?")
    print(f"budget={name!r} cost={cost} budget={budget} target={KILL_PROJECT_ID}")

    if budget <= 0 or cost < budget:
        print("under budget — no action")
        return

    project_name = f"projects/{KILL_PROJECT_ID}"
    if not _is_billing_enabled(project_name):
        print("billing already disabled — nothing to do")
        return

    if DRY_RUN:
        print(f"DRY_RUN: would detach billing from {project_name}")
        return

    print(f"OVER BUDGET — detaching billing from {project_name}")
    print(_disable_billing(project_name))
