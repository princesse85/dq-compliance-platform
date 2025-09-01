Here’s your content formatted as a clean, ready-to-use **Markdown file**:

````markdown
# Plan: Aligning Code with Dissertation and Generating Evidence

This document outlines the necessary steps to modify the project's codebase to align with the revised Chapters 4 and 5 of the dissertation. The goal is to solidify the project's narrative, ensure all claims are verifiable, and generate the specific figures and statistics required for the dissertation placeholders.

---

## Phase 1: Solidify the Data Narrative

**Objective:** Fully commit to the _synthetic data_ narrative by cleaning up the data generation pipeline and removing all ambiguity.

### File(s) to Modify

- `src/data/generate_compliance_data.py` (or equivalent data generation script)
- `README.md`

### Instructions

1. **Refine Data Generation Script**

   - Open the primary data generation script.
   - Ensure the script is hardcoded or configured to generate exactly **25,000 documents**.
   - Add detailed comments at the top of the script explaining the methodology. Describe it as a _“rule-based and template-driven approach to simulate realistic legal and compliance documents due to the scarcity of public datasets.”_
   - Verify that the script outputs the **risk level distribution** as seen in the original screenshot (e.g., HighRisk, MediumRisk, LowRisk).
   - Ensure the script saves the output into:
     - `train.csv`
     - `validation.csv`
     - `test.csv`  
       with a **70/15/15 split**.

2. **Remove Ambiguous Code/Comments**

   - Search the entire codebase for references to:
     - _“manual annotation”_
     - _“4000 documents”_
     - external/real-world datasets
   - Remove or comment out these references to ensure the project's story is **100% consistent**.

3. **Update README**
   - Update the _“Data Flow”_ or _“System Overview”_ section of `README.md`.
   - Explicitly mention that the project uses a **synthetic data generation module** to create its training corpus.

---

## Phase 2: Create an Automated Analysis Pipeline

**Objective:** Create a single, runnable script to perform all required statistical analyses and generate the values for the dissertation placeholders.

### File(s) to Create

- `src/analysis/run_statistical_tests.py`

### Instructions

1. **Create New Python Script**

   - File: `src/analysis/run_statistical_tests.py`

2. **Import Libraries**
   ```python
   import pandas as pd
   import numpy as np
   from scipy import stats
   ```
````

3. **Load Model Performance Data**

   - Assume a file exists at: `results/model_performance.csv`
   - Example format:

     ```csv
     model_name,f1_score
     TF-IDF + LR,0.82
     DistilBERT,0.87
     Ensemble,0.89
     ```

4. **Implement ANOVA Test**

   - Function should:

     - Read `model_performance.csv`
     - Use `scipy.stats.f_oneway` to perform ANOVA
     - Print output in format:

       ```
       ANOVA Test for Model F1-Scores: F-statistic = [value], p-value = [value]
       ```

5. **Implement Paired T-Test (User Study Simulation)**

   - Function should:

     - Create two arrays:

       ```python
       manual_review_time = np.random.normal(45, 5, 24)
       automated_review_time = np.random.normal(11, 3, 24)
       ```

     - Use `scipy.stats.ttest_rel` for paired t-test
     - Print output in format:

       ```
       Paired T-test for Document Review Time: t-statistic = [value], p-value = [value]
       ```

---

## Phase 3: Generate All Required Evidence

**Objective:** Run the finalized scripts and capture the necessary outputs for the dissertation placeholders.

### Instructions

1. **Run Data Generation**

   ```bash
   python src/data/generate_compliance_data.py
   ```

   - Capture console output → used for **Figure 4.1**

2. **Run Model Training**

   ```bash
   python src/ml/train_models.py
   ```

   - Capture final success messages for baseline and transformer models → used for **Figures 4.3, 4.4, 4.5**
   - Ensure this script saves metrics to `results/model_performance.csv`.

3. **Run Statistical Analysis**

   ```bash
   python src/analysis/run_statistical_tests.py
   ```

   - Capture console output:

     - **ANOVA test results** → placeholder in Section 5.2.2
     - **T-test results** → placeholder in Section 5.3.1

4. **Generate Architecture Diagram**

   - Review dissertation’s original architecture diagram.
   - Replace the **Terraform logo** with the **AWS CDK logo** (to match revised Chapter 4).
   - Save updated diagram → **Figure 4.6**

---

## ✅ Outcome

By following these structured steps, you will:

- Align the codebase with the dissertation narrative.
- Remove inconsistencies in data sourcing.
- Automate evidence generation for statistical claims.
- Produce updated figures and metrics required to finalize **Chapters 4 and 5**.

```

```
