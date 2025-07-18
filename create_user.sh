#!/bin/bash
# Usage: ./create_user.sh
# This script creates a new user for the FastAPI app via the /create-user endpoint.
# You will be prompted for admin credentials (existing user) and the new user's username and password.

API_URL="http://localhost:8086/create-user"

read -p "Admin username: " ADMIN_USER
read -s -p "Admin password: " ADMIN_PASS
echo
read -p "New username: " NEW_USER
read -s -p "New password: " NEW_PASS
echo

RESPONSE=$(curl -s -w '\n%{http_code}' -X POST "$API_URL" \
  -u "$ADMIN_USER:$ADMIN_PASS" \
  -H "Content-Type: application/json" \
  -d '{"username": "'$NEW_USER'", "password": "'$NEW_PASS'"}')

BODY=$(echo "$RESPONSE" | head -n -1)
CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$CODE" = "200" ]; then
  echo "User '$NEW_USER' created successfully."
else
  echo "Failed to create user. Server response ($CODE):"
  echo "$BODY"
fi 