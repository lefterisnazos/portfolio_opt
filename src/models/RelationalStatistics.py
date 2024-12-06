import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances
import numpy as np


class RelationalStatistics:
    """
    Module for relational statistic
    """

    def __init__(self, data: pd.DataFrame) -> None:

        """
        Constructor of the RelationalStatistics class.

        Parameters
        ----------
        data : pd.DataFrame
            data of ticker returns 
        ----------
        
        """
        self.data = data

    def calc_standard_deviations(self) -> pd.DataFrame:
        """
        Generates standard deviations for class data

        Parameters
        ----------
        None
        ----------
        Returns a pd.DataFrame of the standard deviations of the data.
        
        """
        return self.data.std()

    def calc_variances(self) -> pd.DataFrame:
        """
        Generates variance for class data

        Parameters
        ----------
        None
        ----------
        Returns a pd.DataFrame of the variance of the data.
        
        """
        return self.data.var()

    def calc_covariance_matrix(self) -> pd.DataFrame:
        """
        Calculates the covariance matrix for the class data

        Parameters
        ----------
        None
        ----------
        Returns a pd.DataFrame of the covariance matrix of the data.
        
        """
        return self.data.cov()

    def calc_correlation_matrix(self) -> pd.DataFrame:
        """
        Generates correlation matrix for class data

        Parameters
        ----------
        None
        ----------
        Returns a pd.DataFrame of the correlation matrix of the data.
        
        """
        return self.data.corr()

    def calc_correlation_distance(self) -> pd.DataFrame:
        """
        Generates correlation distance for class data

        Parameters
        ----------
        None
        ----------
        Returns a pd.DataFrame of the correlation distance of the data.
        
        """
        corr_distance_matrix = (0.5 * (1 - self.calc_correlation_matrix())) ** 0.5
        return corr_distance_matrix

    def calc_eucledian_distance(self) -> pd.DataFrame:
        """
        Calculates eucledian distance for the class data

        Parameters
        ----------
        None
        ----------
        Returns a pd.DataFrame of the eucledian distance of the data.
        
        """
        distance_matrix = self.calc_correlation_distance()
        euclidean_distance_matrix = euclidean_distances(distance_matrix.values)
        matrix_columns = distance_matrix.columns
        euclidean_distance_matrix = pd.DataFrame(euclidean_distance_matrix, index=matrix_columns, columns=matrix_columns)
        return euclidean_distance_matrix

    def calc_shrinkage_coefficient(self) -> float:
        """
        Calculates the shrinkage coefficient for the class data

        Parameters
        ----------
        None
        ----------
        Returns a float of the shrinkage coefficient of the data.
        
        """
        return self.data.shape[1] / self.data.shape[0]

    def calc_average_correlation(self) -> float:
        """
        Generates the average correlation for the class data

        Parameters
        ----------
        None
        ----------
        Returns a float of the average correlation of the data.
        
        """
        correlation = self.calc_correlation_matrix()
        # all diagonal 0
        np.fill_diagonal(correlation.values, 0)

        # Sum up all elements
        sum_of_off_diagonal = correlation.values.sum()

        # calculate the size of the number of values (subtracting the num of rows because we ignore diagonals)
        size = correlation.shape[0] * correlation.shape[1] - correlation.shape[0]

        avg_corr = sum_of_off_diagonal / size

        return avg_corr

    def calc_target_covariance_matrix(self) -> pd.DataFrame:
        """
        Generates the target covariance matrix for the class data

        Parameters
        ----------
        None
        ----------
        Returns a float of the covariance matrix of the data.
        
        """
        sample_cov_matrix = self.calc_covariance_matrix()
        fixed_correlation = self.calc_average_correlation()

        # Extract the variances (diagonal elements)
        variances = np.diag(sample_cov_matrix.values)

        target_cov_matrix = sample_cov_matrix.copy()

        for i in range(sample_cov_matrix.shape[0]):
            for j in range(sample_cov_matrix.shape[1]):
                if i == j:
                    # Keep the variances as is (diagonal elements)
                    target_cov_matrix.iloc[i, j] = variances[i]
                else:
                    # Use the fixed correlation for off-diagonal elements
                    target_cov_matrix.iloc[i, j] = (fixed_correlation * np.sqrt(variances[i] * variances[j]))

        return target_cov_matrix

    def calc_shrinkage_covariance(self) -> pd.DataFrame:
        """
        Generates the shrinkage covariance matrix for the class data

        Parameters
        ----------
        None
        ----------
        Returns a pd.DataFrame of the shrinkage covariance matrix of the data.        
        """
        shrinkage_coefficient = self.calc_shrinkage_coefficient()
        sample_cov_matrix = self.calc_covariance_matrix()
        target_cov_matrix = self.calc_target_covariance_matrix()

        # calculate shrunk covariance matrix
        shrunk_covariance_matrix = (1 - shrinkage_coefficient) * sample_cov_matrix + shrinkage_coefficient * target_cov_matrix
        return shrunk_covariance_matrix
