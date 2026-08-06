# Othniel's Serverless Event Registration & Ticketing

A fully serverless event registration and ticketing web application hosted on AWS, with automated CI/CD deployment via GitHub Actions.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [AWS Services Used](#aws-services-used)
- [Project Structure](#project-structure)
- [CI/CD Pipeline](#cicd-pipeline)
- [GitHub Secrets Setup](#github-secrets-setup)
- [IAM Permissions](#iam-permissions)
- [S3 Bucket Configuration](#s3-bucket-configuration)
- [How to Deploy](#how-to-deploy)
- [Local Development](#local-development)

---

## Project Overview

This is a static frontend web application that allows users to browse events, register, and receive tickets. The frontend is built with plain HTML, CSS, and JavaScript and is hosted on an AWS S3 bucket as a static website. All backend logic is handled by serverless AWS services.

---

## Architecture

```
User Browser
     │
     ▼
Amazon S3 (Static Website Hosting)
     │
     ▼
AWS Lambda (Business Logic)
     │
     ├──▶ Amazon DynamoDB (Event & Registration Data)
     ├──▶ Amazon SNS (Email/SMS Notifications)
     └──▶ Amazon CloudWatch (Logging & Monitoring)
```

---

## AWS Services Used

| Service | Purpose |
|---|---|
| **S3** | Hosts the static frontend (HTML, CSS, JS) |
| **Lambda** | Handles backend logic — registration, ticket generation |
| **DynamoDB** | Stores event data and user registrations |
| **SNS** | Sends confirmation notifications to registered users |
| **CloudWatch** | Monitors Lambda executions and logs errors |

---

## Project Structure

```
Serverless_Event_Registration/
├── .github/
│   └── workflows/
│       └── deploy.yml       # GitHub Actions CI/CD pipeline
├── index.html               # Main frontend application
└── README.md                # Project documentation
```

---

## CI/CD Pipeline

Deployment is automated using **GitHub Actions**. Every push to the `main` branch triggers the pipeline which deploys the site directly to S3.

### Workflow file: `.github/workflows/deploy.yml`

```yaml
name: Deploy to S3

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Upload index.html to S3
        run: |
          aws s3 cp index.html s3://${{ secrets.S3_BUCKET_NAME }}/index.html \
            --content-type "text/html" \
            --cache-control "no-cache, no-store, must-revalidate"

      - name: Sync other assets to S3
        run: |
          aws s3 sync . s3://${{ secrets.S3_BUCKET_NAME }} \
            --exclude ".git/*" \
            --exclude ".github/*" \
            --exclude "index.html" \
            --delete
```

### How it works

1. Code is pushed to the `main` branch
2. GitHub Actions checks out the repository
3. AWS credentials are configured using stored GitHub secrets
4. `index.html` is uploaded with `no-cache` headers to ensure users always get the latest version
5. All other assets are synced to S3, with deleted local files also removed from the bucket

---

## GitHub Secrets Setup

Navigate to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**, and add the following:

| Secret Name | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key ID |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret access key |
| `AWS_REGION` | AWS region e.g. `us-east-1` |
| `S3_BUCKET_NAME` | S3 bucket name e.g. `serverless-event-registration` |

---

## IAM Permissions

The IAM user whose credentials are stored in GitHub secrets must have the following policy attached.

Go to **AWS Console** → **IAM** → **Users** → select your deploy user → **Add permissions** → **Create inline policy** → paste the JSON below:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::YOUR_BUCKET_NAME",
        "arn:aws:s3:::YOUR_BUCKET_NAME/*"
      ]
    }
  ]
}
```

> Replace `YOUR_BUCKET_NAME` with your actual S3 bucket name.

---

## S3 Bucket Configuration

### 1. Enable Static Website Hosting
- Go to your S3 bucket → **Properties** → **Static website hosting**
- Enable it and set **Index document** to `index.html`

### 2. Disable Block Public Access
- Go to **Permissions** → **Block public access** → turn **OFF** all options

### 3. Add Bucket Policy
- Go to **Permissions** → **Bucket Policy** → paste the following:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
    }
  ]
}
```

> Replace `YOUR_BUCKET_NAME` with your actual S3 bucket name.

---

## How to Deploy

### First-time setup

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd Serverless_Event_Registration
git remote -v
```

### Push changes to trigger deployment

```bash
git add .
git commit -m "your commit message"
git push origin main
```

The GitHub Actions pipeline will automatically deploy your changes to S3.

### Monitor deployment
- Go to your GitHub repository → **Actions** tab to see the pipeline running
- Go to **AWS CloudWatch** to monitor Lambda logs and errors

---

## Local Development

Since this is a plain HTML/CSS/JS project, you can open it directly in your browser:

```bash
# Option 1 — open directly
start index.html

# Option 2 — use VS Code Live Server extension
# Right-click index.html → Open with Live Server
```

No build step or package installation is required.

---

## Contributors

- Othniel Asante Takyi
