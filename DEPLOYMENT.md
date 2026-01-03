# Six Figure RAG - AWS ECS Fargate Deployment

This guide covers deploying your RAG application to AWS using ECR, ECS Fargate, and GitHub Actions CI/CD.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS Cloud                                 │
│  ┌─────────────┐    ┌─────────────────────────────────────────┐ │
│  │   GitHub    │    │              VPC                         │ │
│  │   Actions   │    │  ┌─────────────────────────────────────┐│ │
│  │             │    │  │        Application Load Balancer    ││ │
│  └──────┬──────┘    │  └──────────────┬──────────────────────┘│ │
│         │           │                 │                        │ │
│         ▼           │    ┌────────────┼────────────┐          │ │
│  ┌─────────────┐    │    │            │            │          │ │
│  │     ECR     │    │    ▼            ▼            ▼          │ │
│  │  (Images)   │───▶│ ┌──────┐   ┌──────┐   ┌──────────┐     │ │
│  └─────────────┘    │ │FastAPI│   │Next.js│   │ Celery   │     │ │
│                     │ │:8000  │   │:3000  │   │ Workers  │     │ │
│                     │ └──┬───┘   └───────┘   └────┬─────┘     │ │
│                     │    │                        │            │ │
│                     │    └────────┬───────────────┘            │ │
│                     │             ▼                            │ │
│                     │    ┌─────────────────┐                  │ │
│                     │    │ ElastiCache     │                  │ │
│                     │    │ (Redis)         │                  │ │
│                     │    └─────────────────┘                  │ │
│                     └─────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  Supabase   │    │     S3      │    │  Secrets    │        │
│  │  (Database) │    │  (Storage)  │    │  Manager    │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- AWS CLI installed and configured
- Docker installed locally
- GitHub repository for your code
- AWS Account with appropriate permissions

## Project Structure

```
six-figure-rag/
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD pipeline
├── backend/
│   ├── Dockerfile              # FastAPI container
│   ├── Dockerfile.celery       # Celery worker container
│   └── ...
├── frontend/
│   ├── Dockerfile              # Next.js container
│   └── ...
├── ecs/
│   └── task-definitions/
│       ├── backend-task-def.json
│       ├── frontend-task-def.json
│       └── celery-task-def.json
└── scripts/
    └── setup-aws-infrastructure.sh
```

## Step-by-Step Setup

### Step 1: Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Region: ap-south-1 (Mumbai)
# Output format: json
```

### Step 2: Run Infrastructure Setup Script

```bash
chmod +x scripts/setup-aws-infrastructure.sh
./scripts/setup-aws-infrastructure.sh
```

This creates:
- ECR repositories for all services
- CloudWatch log groups
- IAM roles (ecsTaskExecutionRole, ecsTaskRole)
- ECS cluster
- Placeholder secrets in Secrets Manager

### Step 3: Update Secrets in AWS Secrets Manager

Update each secret with your actual values:

```bash
# Database URL (Supabase)
aws secretsmanager put-secret-value \
    --secret-id six-figure-rag/database-url \
    --secret-string "postgresql://user:password@host:5432/database"

# Redis URL (Use ElastiCache or Upstash)
aws secretsmanager put-secret-value \
    --secret-id six-figure-rag/redis-url \
    --secret-string "redis://your-redis-host:6379"

# OpenAI API Key
aws secretsmanager put-secret-value \
    --secret-id six-figure-rag/openai-api-key \
    --secret-string "sk-your-openai-key"

# S3 Bucket Name
aws secretsmanager put-secret-value \
    --secret-id six-figure-rag/s3-bucket \
    --secret-string "your-s3-bucket-name"

# Clerk Secret Key
aws secretsmanager put-secret-value \
    --secret-id six-figure-rag/clerk-secret \
    --secret-string "sk_live_your-clerk-secret"

# Clerk Publishable Key
aws secretsmanager put-secret-value \
    --secret-id six-figure-rag/clerk-publishable-key \
    --secret-string "pk_live_your-clerk-publishable-key"
```

### Step 4: Update Task Definitions

Replace `YOUR_ACCOUNT_ID` in all task definition files:

```bash
# Get your AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Your Account ID: $AWS_ACCOUNT_ID"

# Replace in all files (Linux/Mac)
find ecs/task-definitions -name "*.json" -exec sed -i "s/YOUR_ACCOUNT_ID/$AWS_ACCOUNT_ID/g" {} \;
```

### Step 5: Create VPC and Networking (If not using default VPC)

```bash
# Create VPC with 2 public and 2 private subnets
aws cloudformation create-stack \
    --stack-name six-figure-rag-vpc \
    --template-url https://amazon-eks.s3.us-west-2.amazonaws.com/cloudformation/2020-10-29/amazon-eks-vpc-private-subnets.yaml
```

### Step 6: Set Up Redis (ElastiCache)

```bash
# Create ElastiCache Redis cluster
aws elasticache create-cache-cluster \
    --cache-cluster-id six-figure-rag-redis \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1 \
    --region ap-south-1
```

### Step 7: Create Application Load Balancer

```bash
# Create ALB (via AWS Console is easier)
# 1. Go to EC2 > Load Balancers > Create
# 2. Choose Application Load Balancer
# 3. Configure listeners:
#    - Port 80 -> redirect to 443
#    - Port 443 -> forward to target groups
# 4. Create target groups for backend (8000) and frontend (3000)
```

### Step 8: Register ECS Task Definitions

```bash
aws ecs register-task-definition \
    --cli-input-json file://ecs/task-definitions/backend-task-def.json

aws ecs register-task-definition \
    --cli-input-json file://ecs/task-definitions/frontend-task-def.json

aws ecs register-task-definition \
    --cli-input-json file://ecs/task-definitions/celery-task-def.json
```

### Step 9: Create ECS Services

```bash
# Backend Service
aws ecs create-service \
    --cluster six-figure-rag-cluster \
    --service-name backend-service \
    --task-definition six-figure-rag-backend \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"

# Frontend Service
aws ecs create-service \
    --cluster six-figure-rag-cluster \
    --service-name frontend-service \
    --task-definition six-figure-rag-frontend \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"

# Celery Service
aws ecs create-service \
    --cluster six-figure-rag-cluster \
    --service-name celery-service \
    --task-definition six-figure-rag-celery \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Step 10: Configure GitHub Secrets

Go to your GitHub repo > Settings > Secrets and variables > Actions

Add these secrets:
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key

### Step 11: Push and Deploy

```bash
git add .
git commit -m "Add ECS deployment configuration"
git push origin main
```

The GitHub Action will automatically:
1. Build Docker images for all services
2. Push images to ECR
3. Update ECS services with new images

## CI/CD Pipeline Flow

```
Push to main
    │
    ▼
GitHub Actions triggered
    │
    ▼
Build & Push Job
    ├── Checkout code
    ├── Configure AWS credentials
    ├── Login to ECR
    ├── Build backend image → Push to ECR
    ├── Build frontend image → Push to ECR
    └── Build celery image → Push to ECR
    │
    ▼
Deploy Job
    ├── Update backend task definition
    ├── Deploy backend to ECS
    ├── Update frontend task definition
    ├── Deploy frontend to ECS
    ├── Update celery task definition
    └── Deploy celery to ECS
    │
    ▼
✅ Deployment complete!
```

## Monitoring & Troubleshooting

### View Logs

```bash
# Stream backend logs
aws logs tail /ecs/six-figure-rag-backend --follow

# Stream celery logs
aws logs tail /ecs/six-figure-rag-celery --follow
```

### Check Service Status

```bash
aws ecs describe-services \
    --cluster six-figure-rag-cluster \
    --services backend-service frontend-service celery-service
```

### View Running Tasks

```bash
aws ecs list-tasks --cluster six-figure-rag-cluster
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Task keeps stopping | Check CloudWatch logs for errors |
| Can't pull image | Verify ECR permissions in task execution role |
| Secrets not loading | Check secret ARNs match in task definition |
| Health check failing | Ensure `/health` endpoint exists and returns 200 |

## Cost Optimization Tips

1. **Use Fargate Spot** for Celery workers (can tolerate interruptions)
2. **Right-size tasks** - start small, scale up as needed
3. **Use Application Auto Scaling** for production
4. **Set up budget alerts** in AWS Billing

## Estimated Costs (ap-south-1)

| Resource | Configuration | Est. Monthly Cost |
|----------|--------------|-------------------|
| Fargate (Backend) | 0.5 vCPU, 1GB | ~$15 |
| Fargate (Frontend) | 0.25 vCPU, 0.5GB | ~$8 |
| Fargate (Celery) | 1 vCPU, 2GB | ~$30 |
| ElastiCache (Redis) | cache.t3.micro | ~$12 |
| ALB | Basic | ~$18 |
| **Total** | | **~$83/month** |

## Next Steps for Kubernetes Learning

Once comfortable with this ECS setup, you can:
1. Set up minikube locally
2. Convert these Docker containers to Kubernetes manifests
3. Deploy to EKS using similar CI/CD patterns

Good luck with your deployment! 🚀