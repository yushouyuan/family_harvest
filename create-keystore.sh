#!/bin/bash
# create-keystore.sh

KEYSTORE_NAME="my-release-key.keystore"
KEY_ALIAS="my-key-alias"
KEY_PASSWORD="your_password_here"
KEYSTORE_PASSWORD="your_password_here"
VALIDITY_DAYS=10000

keytool -genkey -v \
  -keystore $KEYSTORE_NAME \
  -alias $KEY_ALIAS \
  -keyalg RSA \
  -keysize 2048 \
  -validity $VALIDITY_DAYS \
  -storepass $KEYSTORE_PASSWORD \
  -keypass $KEY_PASSWORD \
  -dname "CN=Your Name, OU=Development, O=YourCompany, L=City, ST=Province, C=CN"

echo "✅ Keystore 生成完成: $KEYSTORE_NAME"
echo "别名: $KEY_ALIAS"
echo "密码: $KEY_PASSWORD"