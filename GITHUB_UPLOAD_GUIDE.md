# How to Upload This Project to GitHub

## Step 1: Initialize Git Repository Locally

Open your terminal/command prompt and navigate to the project folder:

```bash
cd aws-serverless-pipeline

# Initialize git repository
git init

# Add all files to staging
git add .

# Create initial commit
git commit -m "Initial commit: AWS Serverless Pipeline project"
```

## Step 2: Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click the **+** icon in the top right corner
3. Select **New repository**
4. Fill in the details:
   - **Repository name**: `aws-serverless-pipeline`
   - **Description**: "A serverless data processing pipeline using AWS Lambda, S3, and DynamoDB"
   - **Visibility**: Public (or Private if you prefer)
   - **DO NOT** initialize with README (we already have one)
5. Click **Create repository**

## Step 3: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add GitHub as remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/aws-serverless-pipeline.git

# Rename branch to main (if needed)
git branch -M main

# Push code to GitHub
git push -u origin main
```

## Step 4: Verify Upload

1. Refresh your GitHub repository page
2. You should see all your files uploaded
3. The README.md will automatically display on the repository homepage

## Alternative: Using GitHub Desktop

If you prefer a GUI:

1. Download and install [GitHub Desktop](https://desktop.github.com/)
2. Open GitHub Desktop
3. Click **File** → **Add Local Repository**
4. Select your `aws-serverless-pipeline` folder
5. Click **Publish repository**
6. Choose repository name and visibility
7. Click **Publish Repository**

## Step 5: Update Your Profile README

Now update your GitHub profile README with this project:

```markdown
### 📌 Project 1: AWS Serverless Data Pipeline
- **Description**: Automated data processing pipeline using AWS Lambda, S3, and DynamoDB with serverless architecture
- **Tech Stack**: Python, AWS Lambda, S3, DynamoDB, CloudWatch
- **Status**: 🟢 Active Development
- **Repo**: [aws-serverless-pipeline](https://github.com/YOUR_USERNAME/aws-serverless-pipeline)
```

## Future Updates

To update your repository after making changes:

```bash
# Check status of changes
git status

# Add changed files
git add .

# Commit changes
git commit -m "Description of your changes"

# Push to GitHub
git push
```

## Common Git Commands

```bash
# View commit history
git log

# Create a new branch
git checkout -b feature-name

# Switch between branches
git checkout main

# Pull latest changes from GitHub
git pull

# View remote repository URL
git remote -v
```

## Tips

- Write clear commit messages describing what you changed
- Commit frequently with small, focused changes
- Always pull before pushing to avoid conflicts
- Use `.gitignore` to exclude sensitive files (already included)

## Security Note

⚠️ **NEVER commit AWS credentials or API keys to GitHub!**
- Don't hardcode AWS access keys in your code
- Use environment variables for sensitive data
- The `.gitignore` file already excludes `.env` files
