# HRP Portfolio Optimization

Members:

- Santiago Diaz Tolivia
- Oriol Ripalta I Maso

## Motivation

**Why not simply use MPT (Modern Portfolio Theory)?**
The MPT portfolio optimization model fails to perform well in real settings due to:

1. It involves the estimation of returns for a given set of assets. In real life, estimating returns is very difficult, and small errors in estimation can lead to sub-optimal performance.
2. Mean-variance optimization methods involve the inversion of a covariance matrix for a set of assets. This matrix inversion makes the algorithm susceptible to market volatility and can heavily change the results for small changes in the correlations.

The HRP model solves some of these problems.

# HRP

The HRP portfolio optimization model can be divided into three parts:

1. `Hierarchical Clustering` which breaks down assets into hierarchical clusters
2. `Quasi-Diagonalization` which reorganizes the covariance matrix by placing similar assets together
3. `Recursive Bisection` where weights are assigned to each asset in our portfolio

![HRP Dendogram](https://hudsonthames.org/wp-content/uploads/2020/06/dendrogram.png "HRP Dendogram")

<span style="color:red">Explain different methodologies for clustering!</span>
