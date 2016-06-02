import six
import numpy as np


class JointGaussianDistribution(object):
    """
    In its most common representation, a multivariate Gaussian distribution
    over X1...........Xn is characterized by an n-dimensional mean vector μ,
    and a symmetric nXn covariance matrix Σ.
    This is the base class for its representation.
    """
    def __init__(self, variables, mean_vector, covariance_matrix):
        """
        Parameters
        ----------
        variables: iterable of any hashable python object
            The variables for which the distribution is defined.
        mean_vector: nX1, array like 
            n-dimensional vector where n is the number of variables.
        covariance_matrix: nXn, matrix or 2-d array like
            nXn dimensional matrix where n is the number of variables.

        Examples
        --------
        >>> import numpy as np
        >>> from pgmpy.factors import JointGaussianDistribution as JGD
        >>> dis = JGD(['x1', 'x2', 'x3'], np.array([[1], [-3], [4]])),
                        np.array([[4, 2, -2], [2, 5, -5], [-2, -5, 8]]))
        >>> dis.variables
        ['x1', 'x2', 'x3']
        >>> dis.mean_vector
        np.matrix([[ 1],
                   [-3],
                   [4]]))
        >>> dis.covariance_matrix
        np.matrix([[4, 2, -2],
                   [2, 5, -5],
                   [-2, -5, 8]])
        """
        self.variables = variables
        # dimension of the mean vector and covariance matrix
        n = len(self.variables)

        if len(mean_vector) != n:
            raise ValueError("Length of mean_vector must be equal to the\
                                 number of variables.")

        self.mean_vector = np.matrix(np.reshape(mean_vector, (n, 1)))

        self.covariance_matrix = np.matrix(covariance_matrix)

        if self.covariance_matrix.shape != (n, n):
            raise ValueError("Each dimension of the covariance matrix must\
                                 be equal to the number of variables.")

        self._precision_matrix = None

    @property
    def precision_matrix(self):
        """
        Returns the precision matrix of the distribution.

        Examples
        --------
        >>> import numpy as np
        >>> from pgmpy.factors import JointGaussianDistribution as JGD
        >>> dis = JGD(['x1', 'x2', 'x3'], np.array([[1], [-3], [4]])),
                        np.array([[4, 2, -2], [2, 5, -5], [-2, -5, 8]]))
        >>> dis.precision_matrix
        matrix([[ 0.3125    , -0.125     ,  0.        ],
                [-0.125     ,  0.58333333,  0.33333333],
                [ 0.        ,  0.33333333,  0.33333333]])
        """

        if self._precision_matrix is None:
            self._precision_matrix = np.linalg.inv(self.covariance_matrix)
        return self._precision_matrix

    def marginalize(self, variables, inplace=True):
        """
        Modifies the distribution with marginalized values.

        Parameters
        ----------

        variables: iterator
                List of variables over which to marginalize.
        inplace: boolean
                If inplace=True it will modify the distribution itself,
                else would return a new distribution.

        Returns
        -------
        JointGaussianDistribution or None :
                if inplace=True (default) returns None
                if inplace=False return a new JointGaussianDistribution instance

        Examples
        --------
        >>> from pgmpy.models import JointGaussianDistribution as JGD
        >>> dis = JGD(['x1', 'x2', 'x3'], np.array([[1], [-3], [4]]),
                        np.array([[4, 2, -2], [2, 5, -5], [-2, -5, 8]]))
        >>> dis.variables
        ['x1', 'x2', 'x3']
        >>> dis.mean_vector
        matrix([[ 1],
                [-3],
                [ 4]])
        >>> dis.covariance_matrix
        matrix([[ 4,  2, -2],
                [ 2,  5, -5],
                [-2, -5,  8]])

        >>> dis.marginalize(['x3'])
        dis.variables
        ['x1', 'x2']
        >>> dis.mean_vector
        matrix([[ 1],
                [-3]]))
        >>> dis.covariance_matrix
        np.matrix([[4, 2],
                   [2, 5]])
        """

        if isinstance(variables, six.string_types):
            raise TypeError("variables: Expected type list or array-like, got type str")

        distribution = self if inplace else self.copy()

        var_indexes = [distribution.variables.index(var) for var in variables]
        index_to_keep = sorted(set(range(len(self.variables))) - set(var_indexes))

        distribution.variables = [distribution.variables[index] for index in index_to_keep]
        distribution.mean_vector = distribution.mean_vector[index_to_keep]
        distribution.covariance_matrix = distribution.covariance_matrix[np.ix_(index_to_keep, index_to_keep)]
        distribution._precision_matrix = None

        if not inplace:
            return distribution

    def copy(self):
        """
        Return a copy of the distribution.

        Returns
        -------
        JointGaussianDistribution: copy of the distribution

        Examples
        --------
        >>> import numpy as np
        >>> from pgmpy.models import JointGaussianDistribution as JGD
        >>> gauss_dis = JGD(['x1', 'x2', 'x3'], np.array([[1], [-3], [4]]),
                            np.array([[4, 2, -2], [2, 5, -5], [-2, -5, 8]]))
        >>> copy_dis = gauss_dis.copy()
        >>> copy_dis.variables
        ['x1', 'x2', 'x3']
        >>> copy_dis.mean_vector
        matrix([[ 1],
                [-3],
                [ 4]])
        >>> copy_dis.covariance_matrix
        matrix([[ 4,  2, -2],
                [ 2,  5, -5],
                [-2, -5,  8]])
        >>> copy_dis.precision_matrix
        matrix([[ 0.3125    , -0.125     ,  0.        ],
                [-0.125     ,  0.58333333,  0.33333333],
                [ 0.        ,  0.33333333,  0.33333333]])
        """
        copy_distribution = JointGaussianDistribution(self.variables, self.mean_vector,
                                                      self.covariance_matrix)
        copy_distribution._precision_matrix = self._precision_matrix
        return copy_distribution
