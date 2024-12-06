# Necessary Dependancies
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
import scipy.cluster.hierarchy as sch
from scipy.spatial.distance import squareform
from .RelationalStatistics import RelationalStatistics
from typing import List


class HRP_Calculator:
    """
    Portfolio optimization using Hierarchical Risk Parity (HRP)
    """

    def __init__(self, data, use_shrinkage = True):
        """    
        Constructor of the HRP_Calculator class.
        Initializes the data and stats_module attributes.

        Parameters
        ----------
        data : pd.DataFrame
            A pandas DataFrame of asset returns. NOT COVARIANCE MATRIX.
        use_shrinkage : bool, optional
            A boolean flag to indicate whether to use shrinkage covariance matrix or not.
            The default is True.
        stats_module : RelationalStatistics
            An instance of the RelationalStatistics class. Uses the functions
            in RelationalStatistics to calculate statistics.
        ----------
        """
        self.data = data
        self.stats_module = RelationalStatistics(data)
        self.use_shrinkage = use_shrinkage

    def hierarchical_clustering(self) -> np.ndarray:
        """    
        This function performs hierarchical clustering on the data using eucledian distance.

        Parameters
        ----------
        None
        ----------
        Returns an array of the linkage matrix.
        """
        eucledian_df = self.stats_module.calc_eucledian_distance()
        linkage_matrix = linkage(eucledian_df, 'single')
        return linkage_matrix

    def get_cluster_pairs(self) -> List[tuple[List[int], List[int]]]:
        """
        Get the cluster pairs in order of merging from the linkage matrix.

        Parameters
        ----------
        None
        ----------

        Returns List[Tuple[List[int], List[int]]]: A list of tuples where each tuple contains
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
        
        Parameters
        ----------
        None
        ----------

        Returns list of the merged assets in the order of merging.
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

        Parameters
        ----------
        None
        ----------
        Returns pd.DataFrame: A quasi-diagonalized covariance
        """
        cluster_order = self.get_cluster_order()

        # ensure cluster_order is a 1D array, otherwise flatten
        cluster_order = np.ravel(cluster_order)

        cov_matrix = self.stats_module.calc_shrinkage_covariance() if self.use_shrinkage else self.stats_module.calc_covariance_matrix()

        if isinstance(cov_matrix, pd.DataFrame):  # ensure cov matrix is a pd.DataFrame
            reordered_matrix = cov_matrix.iloc[cluster_order, cluster_order].values
        else:  # else access values using np.ix
            reordered_matrix = cov_matrix[np.ix_(cluster_order, cluster_order)]

        return reordered_matrix

    def calculate_cluster_variance(self, cluster, cov_matrix):
        """
        Calculate the variance for a given cluster by summing the diagonal values
        from the covariance matrix for the assets in the cluster.

        Parameters
        ----------
        cluster : List[int]
            A list of asset indices in the cluster.
        cov_matrix : np.ndarray
            The covariance matrix of the assets.
        ----------

        Returns the total variance of the cluster.
        """
        # If the cluster contains sub-clusters, recursively calculate the variance
        cluster_cov = cov_matrix[np.ix_(cluster, cluster)]

        # Sum the diagonal elements to compute total variance
        total_variance = np.sum(np.diag(cluster_cov))

        return total_variance

    def weights_allocate(self):
        """
        Calculate the weights for the assets in the portfolio using Hierarchical Risk Parity (HRP).
        Makes use of the quasi-diagonalized covariance matrix to allocate weights.

        Parameters
        ----------
        None
        ----------
        Returns Dict[str, float]: A dictionary of asset tickers and their corresponding
        weights in the portfolio.
        """
        # Initialize required variables
        H_clustering = self.hierarchical_clustering()
        stock_order = self.get_cluster_order()
        q_diag = self.quasi_diagonalization()
        cluster_order = self.get_cluster_pairs()
        weights = np.ones(len(stock_order))  # Initialize weights with 1 for all assets
        #cov_matrix = self.stats_module.calc_shrinkage_covariance() if self.use_shrinkage else self.stats_module.calc_covariance_matrix()

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
                    alpha1 = 1 - (left_variance / total_variance)
                    alpha2 = 1 - alpha1

                    # Update the weights for assets in the left and right clusters
                    for asset in left_cluster:
                        weights[asset] *= alpha2  # Update weight for asset in left cluster

                    for asset in right_cluster:
                        weights[asset] *= alpha1  # Update weight for asset in right cluster

            return weights

        final_weights = allocate_recursive(cluster_order, weights)

        # Create a dictionary with asset names as keys
        # Assuming stock_order refers to indices of the data, map indices to the column names in data
        weights_dict = {self.data.columns[stock_order[i]]: float(final_weights[i]) for i in range(len(stock_order))}

        return weights_dict


class HRP_Calculator_2:
    """
    Hierarchical Risk Parity (HRP) implementation using scipy for clustering.
    """

    def __init__(self, returns: pd.DataFrame):
        self.returns = returns

    def calculate_correlation_distance(self) -> np.ndarray:
        """
        Calculate the pairwise correlation distance (1 - correlation).

        Returns:
            np.ndarray: Condensed distance matrix.
        """
        corr = self.returns.corr().values
        dist = ((1 - corr)/2.)**0.5

        # Ensure symmetry
        dist = (dist + dist.T) / 2
        return squareform(dist)

    def perform_clustering(self) -> np.ndarray:
        """
        Perform hierarchical clustering using the correlation distance.

        Returns:
            np.ndarray: Linkage matrix for hierarchical clustering.
        """
        dist_matrix = self.calculate_correlation_distance()
        return linkage(dist_matrix, method='single')  # Single linkage clustering

    def get_quasi_diagonal_order(self, linkage_matrix: np.ndarray) -> list:
        """
        Get the hierarchical ordering of assets based on the linkage matrix.

        Args:
            linkage_matrix (np.ndarray): Linkage matrix from hierarchical clustering.

        Returns:
            list: Ordered list of asset indices.
        """
        dendro = dendrogram(linkage_matrix, no_plot=True)
        return dendro['leaves']

    def weights_allocate(self) -> pd.Series:
        """
        Calculate asset weights using Hierarchical Risk Parity.

        Returns:
            pd.Series: HRP weights for the portfolio, indexed by asset names.
        """
        # Covariance matrix
        cov = self.returns.cov().values
        linkage_matrix = self.perform_clustering()
        sorted_indices = self.get_quasi_diagonal_order(linkage_matrix)

        # Quasi-diagonalized covariance matrix
        ordered_cov = cov[np.ix_(sorted_indices, sorted_indices)]
        ordered_assets = self.returns.columns[sorted_indices]

        # Calculate HRP weights
        weights = pd.Series(1, index=ordered_assets)
        clusters = [ordered_assets.tolist()]

        while len(clusters) > 0:
            cluster = clusters.pop(0)
            if len(cluster) == 1:
                continue

            # Split cluster into two halves
            left_cluster = cluster[:len(cluster) // 2]
            right_cluster = cluster[len(cluster) // 2:]

            # Calculate variance of each cluster
            left_var = self._cluster_variance(ordered_cov, left_cluster)
            right_var = self._cluster_variance(ordered_cov, right_cluster)

            # Allocate weights inversely proportional to variance
            total_var = left_var + right_var
            weights[left_cluster] *= right_var / total_var
            weights[right_cluster] *= left_var / total_var

            # Add sub-clusters to the queue
            clusters.append(left_cluster)
            clusters.append(right_cluster)

        return weights.sort_index()

    def _cluster_variance(self, cov: np.ndarray, cluster: list) -> float:
        """
        Calculate the variance of a cluster based on the covariance matrix.

        Args:
            cov (np.ndarray): Covariance matrix.
            cluster (list): List of asset indices or tickers in the cluster.

        Returns:
            float: Cluster variance.
        """
        # Map tickers to their integer positions if cluster contains strings
        if isinstance(cluster[0], str):
            cluster = [self.returns.columns.get_loc(ticker) for ticker in cluster]

        # Extract the sub-matrix for the cluster
        cluster_cov = cov[np.ix_(cluster, cluster)]
        weights = np.ones(len(cluster))  # Equal weights for the cluster
        return np.dot(weights, np.dot(cluster_cov, weights))

    def plot_dendrogram(self):
        """
        Plot the hierarchical clustering dendrogram.
        """
        linkage_matrix = self.perform_clustering()
        dendrogram(linkage_matrix, labels=self.returns.columns.tolist())


class HRP_Calculator_3:
    """
    Hierarchical Risk Parity (HRP) implementation based on Lopez de Prado's code.
    """

    def __init__(self, returns: pd.DataFrame):
        """
        Initialize with a DataFrame of asset returns.
        """
        self.returns = returns
        self.cov = returns.cov()
        self.corr = returns.corr()

    @staticmethod
    def get_ivp(cov: pd.DataFrame) -> np.ndarray:
        """
        Compute the inverse-variance portfolio.
        """
        ivp = 1.0 / np.diag(cov)
        ivp /= ivp.sum()
        return ivp

    @staticmethod
    def get_cluster_var(cov: pd.DataFrame, cluster_items: list) -> float:
        """
        Compute the variance per cluster.
        """
        # Map integer indices to labels if needed
        if isinstance(cluster_items[0], int):  # Check if indices are integers
            cluster_items = cov.index[cluster_items]  # Map to labels

        cov_ = cov.loc[cluster_items, cluster_items]  # Slice covariance matrix
        w_ = HRP_Calculator_3.get_ivp(cov_).reshape(-1, 1)
        cluster_var = np.dot(np.dot(w_.T, cov_), w_)[0, 0]
        return cluster_var

    @staticmethod
    def get_quasi_diag(linkage: np.ndarray) -> list:
        """
        Sort clustered items by distance.
        """
        linkage = linkage.astype(int)
        sort_ix = pd.Series([linkage[-1, 0], linkage[-1, 1]])
        num_items = linkage[-1, 3]  # Number of original items

        while sort_ix.max() >= num_items:
            sort_ix.index = range(0, sort_ix.shape[0] * 2, 2)  # Make space
            clusters = sort_ix[sort_ix >= num_items]  # Find clusters
            i = clusters.index
            j = clusters.values - num_items
            sort_ix[i] = linkage[j, 0]  # Item 1
            new_clusters = pd.Series(linkage[j, 1], index=i + 1)
            sort_ix = pd.concat([sort_ix, new_clusters])   # Item 2
            sort_ix = sort_ix.sort_index()  # Re-sort
            sort_ix.index = range(sort_ix.shape[0])  # Re-index
        return sort_ix.tolist()

    def get_rec_bipart(self, sort_ix: list) -> pd.Series:
        """
        Compute HRP allocation.
        """
        # Convert integer indices to labels
        sort_ix = self.returns.columns[sort_ix]

        w = pd.Series(1, index=sort_ix)
        clusters = [sort_ix.tolist()]  # Initialize all items in one cluster

        while len(clusters) > 0:
            clusters = [cluster[j:k] for cluster in clusters for j, k in ((0, len(cluster) // 2), (len(cluster) // 2, len(cluster))) if len(cluster) > 1]  # Bi-section
            for i in range(0, len(clusters), 2):  # Parse in pairs
                cluster_0 = clusters[i]  # Cluster 1
                cluster_1 = clusters[i + 1]  # Cluster 2
                var_0 = self.get_cluster_var(self.cov, cluster_0)
                var_1 = self.get_cluster_var(self.cov, cluster_1)
                alpha = 1 - var_0 / (var_0 + var_1)
                w[cluster_0] *= alpha  # Weight 1
                w[cluster_1] *= 1 - alpha  # Weight 2
        return w

    @staticmethod
    def correl_dist(corr: pd.DataFrame) -> pd.DataFrame:
        """
        A distance matrix based on correlation.
        """
        dist = ((1 - corr) / 2.0) ** 0.5  # Distance matrix
        return dist

    def weights_allocate(self) -> pd.Series:
        """
        Perform the full HRP process and return the portfolio weights.
        """
        dist = self.correl_dist(self.corr)
        linkage_matrix = sch.linkage(squareform(dist), method="single")
        sort_ix = self.get_quasi_diag(linkage_matrix)
        hrp_weights = self.get_rec_bipart(sort_ix)
        return hrp_weights.sort_index()

# Usage Example
# if __name__ == "__main__":
#     # Mock data
#     np.random.seed(42)
#     data = pd.DataFrame(np.random.randn(100, 5), columns=["A", "B", "C", "D", "E"])
#     hrp = HRP_Calculator(data)
#     weights = hrp.weights_allocate()
#     print(weights)

