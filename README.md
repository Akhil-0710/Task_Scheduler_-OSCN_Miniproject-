# Task_Scheduler_-OSCN_Miniproject-

# 🚀 Collaboration Workflow Guide

## 📌 Why We Are Using This Workflow

When multiple people work on the same codebase, directly editing the main code can lead to:

* Broken functionality
* Conflicting changes
* Loss of stable versions
* Difficulty tracking who changed what

To avoid this, we follow a structured GitHub workflow that ensures:

* The `main` branch always remains stable and working
* Everyone can experiment and build features independently
* Changes are reviewed before being added to the main project
* We maintain clean, trackable progress

---

## 🧠 Basic Concept

We divide work into:

* **Main Branch (`main`)**
  → Stable, production-ready code
  → No direct changes allowed

* **Feature Branches (`feature/...`)**
  → Individual work by each team member
  → Safe space to experiment and build

* **Pull Requests (PRs)**
  → Used to propose changes from a branch to `main`
  → Reviewed before merging

---

## ⚙️ How to Work (Step-by-Step)

### 1. Clone the Repository

```bash
git clone <repo-url>
cd <repo-name>
```

---

### 2. Create Your Own Branch

Always create a new branch before starting work:

```bash
git checkout -b feature/<your-feature-name>
```

Example:

```bash
git checkout -b feature/login-system
```

---

### 3. Make Changes and Commit

```bash
git add .
git commit -m "Add login system"
```

---

### 4. Push Your Branch

```bash
git push origin feature/<your-feature-name>
```

---

### 5. Create a Pull Request

* Go to GitHub
* Click **"Compare & Pull Request"**
* Add description of your changes
* Submit PR

---

### 6. Review Process

* Team members review the code
* Suggestions or changes may be requested
* Once approved → PR is merged into `main`

---

## ⚠️ Important Rules

* ❌ Do NOT push directly to `main`
* ✅ Always create a separate branch
* ✅ Keep changes small and focused
* ✅ Pull latest changes before starting work:

  ```bash
  git pull origin main
  ```

---

## 🔄 Workflow Summary

1. Create branch
2. Make changes
3. Push branch
4. Create Pull Request
5. Review & approve
6. Merge into `main`

---

## 🎯 Goal

This workflow ensures:

* Stability of the project
* Smooth collaboration
* Clear tracking of contributions
* Reduced conflicts and errors

---

Following this process is mandatory for all contributors.
