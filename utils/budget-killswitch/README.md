# Budget kill switch

A Cloud Billing budget **only sends alerts** — it does not stop spend. This turns the
budget into a real cap: on the Pub/Sub notification, it detaches billing from the target
project, which halts every billable resource in it.

Already done (see PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md):

- Pub/Sub topic `projects/local-embeddings-inc-temp-vm/topics/budget-alerts`
- Budget "Local Embeddings inc. temp VM" ($15/mo) wired to publish to it

Remaining steps need privileged IAM and must be run by a human.

## 1. Service account with billing admin

```bash
P=local-embeddings-inc-temp-vm
B=013B44-FED68D-98FB8C
SA="budget-killswitch@$P.iam.gserviceaccount.com"

gcloud iam service-accounts create budget-killswitch \
    --project="$P" --display-name="Budget kill switch"

# Privileged: lets the function detach billing.
gcloud billing accounts add-iam-policy-binding "$B" \
    --member="serviceAccount:$SA" --role="roles/billing.admin"
```

## 2. Enable the deploy APIs

```bash
gcloud services enable cloudfunctions.googleapis.com cloudbuild.googleapis.com \
    run.googleapis.com artifactregistry.googleapis.com eventarc.googleapis.com \
    --project="$P"
```

## 3. Deploy

Deploy with `DRY_RUN=1` first and confirm the logs before arming it for real.

```bash
gcloud functions deploy budget-killswitch \
    --gen2 --runtime=python311 --region=us-central1 \
    --source=utils/budget-killswitch --entry-point=stop_billing \
    --trigger-topic=budget-alerts \
    --service-account="$SA" \
    --set-env-vars="KILL_PROJECT_ID=$P,DRY_RUN=1" \
    --project="$P"
```

Arm it by redeploying with `DRY_RUN=0`.

## 4. Test without spending $15

Publish a synthetic over-budget notification:

```bash
gcloud pubsub topics publish budget-alerts --project="$P" \
    --message='{"budgetDisplayName":"test","costAmount":999,"budgetAmount":15}'

gcloud functions logs read budget-killswitch --region=us-central1 --project="$P" --limit=20
```

With `DRY_RUN=1` you should see `DRY_RUN: would detach billing from projects/...`.

## Caveats

- **Detaching billing is destructive** and stops every billable resource in the target
  project. Only point `KILL_PROJECT_ID` at a disposable project.
- Budget data is **not real-time** — Cloud Billing reports lag, so spend can overshoot the
  threshold before the notification fires. This is a backstop, not a hard ceiling.
- Re-enabling requires manually re-linking a billing account to the project.
