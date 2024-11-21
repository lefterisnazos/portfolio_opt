# Necessary Dependancies
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from .RelationalStatistics import RelationalStatistics
from typing import List


class HRP_Calculator:
    """
    Portfolio optimization using Hierarchical Risk Parity (HRP)
    """

    def __init__(self, data):
        """
        pd.DataFrame data: data of ticker returns
        class RelationalStatistics: module for relational statistics
        """
        self.data = data
        self.stats_module = RelationalStatistics(data)

    def hierarchical_clustering(self) -> np.ndarray:
        """
        Performs hierarchical clustering on the euclidean distance matrix.
        """
        eucledian_df = self.stats_module.calc_eucledian_distance()
        linkage_matrix = linkage(eucledian_df, 'single')
        return linkage_matrix

    def get_cluster_pairs(self) -> List[tuple[List[int], List[int]]]:
        """
        Get the cluster pairs in order of merging from the linkage matrix.

        Returns:
            List[Tuple[List[int], List[int]]]: A list of tuples where each tuple contains
                                               the left and right clusters being merged.
        """
        linkage_matrix = self.hierarchical_clustering()
        n_assets = linkage_matrix.shape[0] + 1  # Number of original assets (leaf nodes)
        cluster_map = {i: [i] for i in range(n_assets)}  # Map to track clusters

        cluster_pairs = []

        for row in linkage_matrix:
            left, right = int(row[0]), int(row[1])
            # Get the clusters being merged
            left_cluster = cluster_map[left] if left < n_assets else cluster_map[left]
            right_cluster = cluster_map[right] if right < n_assets else cluster_map[right]

            # Record the pair of clusters being merged
            cluster_pairs.append((left_cluster, right_cluster))

            # Merge clusters and assign to a new cluster ID
            new_cluster = left_cluster + right_cluster
            cluster_map[len(cluster_map)] = new_cluster

        return cluster_pairs

    def get_cluster_order(self) -> List[str]:
        """
        Gets the cluster order from the hierarchical clustering.
        """
        n = self.data.shape[1]  # total number of assets
        linkage_matrix = self.hierarchical_clustering()
        merged_assets = []  # assets
        merged_set = set()  # cache for assets

        for i in range(len(linkage_matrix)):  # iterate through the linkage matrix
            left, right = int(linkage_matrix[i, 0]), int(linkage_matrix[i, 1])

            # add one ticker to the merged list if not merged already
            if left < n and left not in merged_set:
                merged_assets.append(left)
                merged_set.add(left)

            if right < n and right not in merged_set:
                merged_assets.append(right)
                merged_set.add(right)

        return merged_assets

    def quasi_diagonalization(self) -> pd.DataFrame:
        """
        Use the linkage matrix and cluster order to quasi-diagonalize the covariance matrix.
        Such that the highest correlations are along the diagonal.
        """
        cluster_order = self.get_cluster_order()

        # ensure cluster_order is a 1D array, otherwise flatten
        cluster_order = np.ravel(cluster_order)
        cov_matrix = self.stats_module.calc_covariance_matrix()

        if isinstance(cov_matrix, pd.DataFrame):  # ensure cov matrix is a pd.DataFrame
            reordered_matrix = cov_matrix.iloc[cluster_order, cluster_order].values
        else:  # else access values using np.ix
            reordered_matrix = cov_matrix[np.ix_(cluster_order, cluster_order)]

        return reordered_matrix

    def calculate_cluster_variance(self, cluster, cov_matrix):
        """
        Calculate the variance for a given cluster by summing the diagonal values
        from the covariance matrix for the assets in the cluster.
        """
        # If the cluster contains sub-clusters, recursively calculate the variance
        if isinstance(cluster, list):
            # For numpy arrays, we use numpy indexing to select the relevant sub-matrix
            cluster_cov = cov_matrix[np.ix_(cluster, cluster)]
            # Sum the diagonal to get the variance
            return np.sum(np.diagonal(cluster_cov))
        else:
            # If it's just a single asset, return its variance
            return cov_matrix[cluster, cluster]

    def weights_allocate(self):
        # Initialize required variables
        H_clustering = self.hierarchical_clustering()
        stock_order = self.get_cluster_order()
        q_diag = self.quasi_diagonalization()
        cluster_order = self.get_cluster_pairs()
        weights = np.ones(len(stock_order))  # Initialize weights with 1 for all assets

        def allocate_recursive(cluster_order, weights):
            # Iterate through cluster pairs in reversed order
            for pair in reversed(cluster_order):
                left_cluster = pair[0]
                right_cluster = pair[1]

                # If the left or right cluster contains more sub-clusters, recurse into it
                if isinstance(left_cluster[0], list):  # Left cluster has sub-clusters
                    allocate_recursive(left_cluster, weights)
                else:  # Left cluster is a leaf node (individual assets)
                    left_variance = self.calculate_cluster_variance(left_cluster, q_diag)
                    right_variance = self.calculate_cluster_variance(right_cluster, q_diag)

                    total_variance = left_variance + right_variance
                    alpha1 = left_variance / total_variance
                    alpha2 = right_variance / total_variance

                    # Update the weights for assets in the left and right clusters
                    for asset in left_cluster:
                        weights[stock_order.index(asset)] *= alpha1  # Update weight for asset in left cluster

                    for asset in right_cluster:
                        weights[stock_order.index(asset)] *= alpha2  # Update weight for asset in right cluster

            return weights

        final_weights = allocate_recursive(cluster_order, weights)

        # Create a dictionary with asset names as keys
        # Assuming stock_order refers to indices of the data, map indices to the column names in data
        weights_dict = {self.data.columns[stock_order[i]]: float(final_weights[i]) for i in range(len(stock_order))}

        return weights_dict

