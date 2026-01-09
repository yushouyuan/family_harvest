#!/bin/bash
# 验证 GitHub secrets 是否已正确配置
# 需要 gh CLI：https://cli.github.com/

echo "Checking GitHub repository secrets..."

REQUIRED_SECRETS=(
  "KEYSTORE_BASE64"
  "KEY_ALIAS"
  "KEYSTORE_PASSWORD"
  "KEY_PASSWORD"
)

MISSING=0

for secret in "${REQUIRED_SECRETS[@]}"; do
  if gh secret list | grep -q "^$secret"; then
    echo "✓ Secret '$secret' is configured"
  else
    echo "✗ Secret '$secret' is MISSING"
    MISSING=$((MISSING + 1))
  fi
done

if [ $MISSING -eq 0 ]; then
  echo ""
  echo "All required secrets are configured!"
  echo ""
  echo "Next steps:"
  echo "1. Push changes to main: git push origin main"
  echo "2. Visit GitHub Actions tab and watch the workflow run"
  echo "3. Download APK from Release once build is complete"
else
  echo ""
  echo "ERROR: $MISSING secret(s) missing. Add them in GitHub Settings → Secrets and variables → Actions"
  exit 1
fi
