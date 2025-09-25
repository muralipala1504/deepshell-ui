# Deepshell-UI Prompt Test Log

This file tracks test prompts to verify domain filtering, precision, and output formatting.  
✅ = Allowed & correct response  
🚫 = Correctly rejected (out of domain)  
🟡 = Leak (responded when should have been rejected)

---

## ✅ Allowed (Infra/DevOps)
- "docker ps -a" → ✅ command output
- "Terraform script to create AWS S3 bucket" → ✅ hcl output
- "Ansible playbook to install nginx" → ✅ yaml output
- "Generate shell script for LVM with 20GB space" → ✅ bash output
- "Chef recipe to configure Apache (infra context)" → ✅ ruby output
- "Kubernetes manifest for nginx Pod" → ✅ yaml output

---

## 🚫 Blocked (Out of Domain)
- "Recipe for chicken biryani" → 🚫 refused
- "Explain Agile methodology" → 🚫 refused
- "Game of Thrones plot summary" → 🚫 refused
- "Stock market forecast" → 🚫 refused

---

## 🟡 Leaks (Need Fix)
- "Love poem about clouds" → 🟡 generated poem (should be refused)

---

## Notes
- Continue testing diverse prompts daily.  
- Update this file so we can patch leaks in **Sunday Sprint (v1.2.0)**.
