"""
Pre-loaded high-quality sample study notes for instant testing and demonstration.
"""

SAMPLE_NOTES = {
    "Artificial Intelligence & Machine Learning": """# Introduction to Artificial Intelligence and Machine Learning

## 1. Core Definitions
Artificial Intelligence (AI) is the broader discipline of creating machines capable of performing tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and translation between languages.

Machine Learning (ML) is a subset of AI focused on building algorithms that learn patterns from data and improve their performance on a specific task over time without being explicitly programmed.

Deep Learning (DL) is a further subset of Machine Learning based on Artificial Neural Networks with multiple representation layers (deep architectures) inspired by biological neural circuits in human brains.

## 2. Paradigms of Machine Learning
### Supervised Learning
- The model is trained on labeled data consisting of input-output pairs $(X, Y)$.
- Goal: Learn a mapping function $f: X \rightarrow Y$.
- Tasks:
  - Regression: Predicting continuous numerical values (e.g., house prices, temperature forecasting).
  - Classification: Assigning inputs into discrete categories (e.g., spam detection, disease diagnosis).
- Algorithms: Linear Regression, Logistic Regression, Support Vector Machines (SVM), Random Forests, XGBoost, Multilayer Perceptrons.

### Unsupervised Learning
- The model discovers hidden patterns, groupings, or representations within unlabeled data $(X)$.
- Tasks:
  - Clustering: Grouping similar instances together (e.g., K-Means, DBSCAN, Hierarchical Clustering).
  - Dimensionality Reduction: Compressing features while preserving maximal variance (e.g., Principal Component Analysis - PCA, t-SNE).
  - Association Rule Mining: Discovering relationships between variables (e.g., Apriori algorithm).

### Reinforcement Learning (RL)
- An agent interacts with a dynamic environment through sequential actions to maximize cumulative numerical reward.
- Core components: Agent, Environment, State ($s$), Action ($a$), Reward ($r$), Policy ($\pi$).
- Famous examples: AlphaGo, autonomous driving control, robotic manipulation.

## 3. The Model Training Lifecycle
1. Data Collection & Ingestion: Gathering representative, unbiased datasets.
2. Data Preprocessing & Cleaning: Handling missing values, outlier detection, normalization/standardization.
3. Feature Engineering: Selecting, extracting, and transforming variables to improve model signal.
4. Model Selection & Architecture Design: Choosing appropriate algorithms based on problem complexity.
5. Training & Optimization: Minimizing a Loss Function using optimization algorithms such as Stochastic Gradient Descent (SGD) or Adam.
6. Evaluation & Validation: Assessing generalization on unseen data using metrics like Precision, Recall, F1-Score, ROC-AUC, and Mean Squared Error (MSE).
7. Hyperparameter Tuning: Grid search, Random search, or Bayesian optimization for tuning parameters not learned during training.
8. Deployment & Monitoring: Serving predictions via APIs and detecting concept drift over time.

## 4. Key Challenges & Terminology
- Overfitting: When a model learns noise and details of the training set too well, failing to generalize to new data (high variance). Mitigations include regularization (L1/L2), dropout, and cross-validation.
- Underfitting: When a model is too simple to capture the underlying structure of the data (high bias).
- Bias-Variance Tradeoff: The fundamental balance between model simplicity (bias) and sensitivity to training data fluctuations (variance).
- Gradient Descent: An iterative optimization algorithm used to find the local minimum of a differentiable function.
""",

    "Cell Biology & Bioenergetics": """# Fundamentals of Cell Biology and Bioenergetics

## 1. Cell Theory and Organization
The Cell Theory stands as one of the foundational pillars of modern biology:
1. All living organisms are composed of one or more cells.
2. The cell is the basic structural and functional unit of life.
3. All cells arise from pre-existing cells through division.

Cells are broadly categorized into two fundamental domains:
- Prokaryotic Cells: Unicellular organisms lacking a membrane-bound nucleus and membrane-enclosed organelles (e.g., Bacteria, Archaea). Genetic material resides in an irregularly shaped region called the nucleoid.
- Eukaryotic Cells: Organisms with complex internal structures including a distinct membrane-bound nucleus housing genomic DNA, along with specialized organelles (e.g., Animals, Plants, Fungi, Protists).

## 2. Key Organelles and Their Functions
- Nucleus: The control center of eukaryotic cells; stores genomic DNA and directs protein synthesis via transcription of mRNA.
- Mitochondria: Often termed the "powerhouse of the cell"; double-membraned organelles that generate adenosine triphosphate (ATP) via aerobic cellular respiration and oxidative phosphorylation.
- Ribosomes: Non-membrane-bound complexes of ribosomal RNA (rRNA) and proteins that translate mRNA transcripts into polypeptide chains.
- Endoplasmic Reticulum (ER):
  - Rough ER: Studded with ribosomes; synthesizes and processes proteins destined for membranes or secretion.
  - Smooth ER: Lacks ribosomes; synthesizes lipids, phospholipids, and steroid hormones, while detoxifying metabolic byproducts.
- Golgi Apparatus: Series of flattened membranous sacs (cisternae) that modify, package, sort, and tag proteins for cellular delivery or exocytosis.
- Lysosomes: Spherical vesicles containing acidic hydrolases that digest macromolecules, cellular debris, and foreign pathogens.
- Chloroplasts (Plant cells): Double-membrane plastids containing chlorophyll pigments that capture photon energy to conduct photosynthesis.

## 3. Cellular Respiration and Energy Production
Aerobic cellular respiration converts biochemical energy from glucose into ATP through four sequential metabolic stages:
$$\\text{C}_6\\text{H}_{12}\\text{O}_6 + 6\\text{O}_2 \\rightarrow 6\\text{CO}_2 + 6\\text{H}_2\\text{O} + \\sim 30-32\\text{ ATP}$$

1. Glycolysis (Cytoplasm):
   - Glucose (6-carbon molecule) is enzymatically split into two molecules of pyruvate (3-carbon).
   - Net yield: 2 ATP (via substrate-level phosphorylation) and 2 NADH.
   - Occurs anaerobically (does not require molecular oxygen).

2. Pyruvate Oxidation (Mitochondrial Matrix):
   - Pyruvate is converted to Acetyl-CoA, releasing $\\text{CO}_2$ and yielding 1 NADH per pyruvate (2 NADH per glucose).

3. The Citric Acid Cycle / Krebs Cycle (Mitochondrial Matrix):
   - Acetyl-CoA combines with oxaloacetate to form citrate.
   - For every glucose molecule (two turns of the cycle): 2 ATP/GTP, 6 NADH, 2 $\\text{FADH}_2$, and 4 $\\text{CO}_2$ are produced.

4. Oxidative Phosphorylation & Electron Transport Chain (Inner Mitochondrial Membrane):
   - High-energy electrons from NADH and $\\text{FADH}_2$ traverse protein complexes (I-IV).
   - Electron transfer drives proton ($\text{H}^+$) pumping across the inner membrane into the intermembrane space, creating an electrochemical gradient (proton-motive force).
   - Chemiosmosis: Protons flow down their gradient through ATP Synthase, driving phosphorylation of ADP into ATP.
   - Oxygen serves as the terminal electron acceptor, bonding with protons to form $\\text{H}_2\\text{O}$.
""",

    "World History: The Industrial Revolution": """# The Industrial Revolution: Transformation of Global Society

## 1. Overview and Chronology
The Industrial Revolution marked the profound transition from agrarian, handicraft-based economies to mechanized industrial manufacturing dominated by powered machinery, specialized factories, and mass production.

Historians typically divide the era into two primary waves:
- First Industrial Revolution (c. 1760 – 1840): Originated in Great Britain; characterized by the mechanization of textile spinning and weaving, commercial adoption of the steam engine, iron metallurgy improvements, and canal/railway infrastructure expansion.
- Second Industrial Revolution / Technological Revolution (c. 1870 – 1914): Spread across Western Europe, the United States, and Japan; defined by mass steel production (Bessemer process), electrification, synthetic chemical production, assembly line mass manufacturing, and the internal combustion engine.

## 2. Why Did It Begin in Great Britain?
Britain possessed a unique convergence of geographic, institutional, and economic advantages:
1. Abundant Natural Resources: Rich domestic deposits of coal (essential fuel) and iron ore located in close geographic proximity.
2. Agricultural Revolution: Preceding agricultural innovations (crop rotation, selective breeding, Jethro Tull's seed drill) dramatically increased food yields, reducing farm labor requirements and freeing a demographic labor surplus for industrial centers.
3. Capital Accumulation & Financial Institutions: Sophisticated banking institutions, the Bank of England, established credit networks, and global trade wealth.
4. Stable Legal and Political Environment: Rule of law, patent protection laws that incentivized inventors, and secure private property rights following the Glorious Revolution (1688).
5. Global Colonial Empire: Access to raw materials (e.g., colonial American and Indian cotton) and captive export consumer markets across global colonies.

## 3. Transformative Technological Inventions
- Flying Shuttle (John Kay, 1733): Doubled weaver productivity, sparking a yarn bottleneck.
- Spinning Jenny (James Hargreaves, 1764): Enabled a single worker to spin multiple spools of thread simultaneously.
- Water Frame (Richard Arkwright, 1769): Utilized waterwheels to drive spinning machines, giving birth to the centralized modern factory system.
- Steam Engine (James Watt & Matthew Boulton, 1769-1776): Improved Newcomen's primitive atmospheric engine by introducing a separate condenser, dramatically increasing fuel efficiency and untethering factories from riverbanks.
- Power Loom (Edmund Cartwright, 1785): Mechanized the weaving process to match explosive spinning yarn outputs.

## 4. Socioeconomic and Environmental Impacts
### Urbanization and Working Conditions
- Massive rural-to-urban migration led to the explosive growth of industrial cities (e.g., Manchester, Birmingham, Leeds).
- Rapid urban growth overwhelmed municipal infrastructure, producing squalid tenements, contaminated water supplies, cholera outbreaks, and dense air pollution ("smog").
- Working classes endured 12-to-16-hour workdays, dangerous factory machinery lacking safety guards, and widespread child labor in coal mines and cotton mills.

### Rise of New Economic Theories
- Capitalism & Laissez-Faire: Adam Smith published *The Wealth of Nations* (1776), advocating free-market dynamics, the division of labor, and minimal state intervention.
- Socialism & Marxism: In response to rampant worker exploitation, Karl Marx and Friedrich Engels published *The Communist Manifesto* (1848), critiquing the bourgeois ownership of the means of production and forecasting proletarian revolution.
- Labor Unions & Legislative Reform: Workers organized trade unions and agitated for legal protections, leading to Britain's Factory Acts (limiting child working hours) and public health legislation.
"""
}
