import numpy as np
import pandas as pd

class DecisionTreeClassifier:
    """
    A decision tree classifier.

    Attributes:
        max_depth (int): The maximum depth of the tree.
        min_samples_split (int): The minimum number of samples required to split an internal node.
        tree (dict): The decision tree represented as a nested dictionary.
    """

    def __init__(self, max_depth=None, min_samples_split=2):
        """
        Initializes the DecisionTreeClassifier.

        Args:
            max_depth (int, optional): The maximum depth of the tree. Defaults to None (unlimited depth).
            min_samples_split (int, optional): The minimum number of samples required to split an internal node. Defaults to 2.
        """
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = {}

    def _calculate_entropy(self, y):
        """
        Calculates the entropy of a set of labels.

        Args:
            y (np.ndarray): The labels.

        Returns:
            float: The entropy.
        """
        probabilities = np.bincount(y) / len(y)
        entropy = -np.sum([p * np.log2(p) for p in probabilities if p > 0])
        return entropy

    def _information_gain(self, y, y_left, y_right):
        """
        Calculates the information gain from splitting a set of labels into two subsets.

        Args:
            y (np.ndarray): The original labels.
            y_left (np.ndarray): The labels of the left subset.
            y_right (np.ndarray): The labels of the right subset.

        Returns:
            float: The information gain.
        """
        entropy_parent = self._calculate_entropy(y)
        n = len(y)
        n_left = len(y_left)
        n_right = len(y_right)
        entropy_left = self._calculate_entropy(y_left) if n_left > 0 else 0
        entropy_right = self._calculate_entropy(y_right) if n_right > 0 else 0
        information_gain = entropy_parent - (n_left / n * entropy_left) - (n_right / n * entropy_right)
        return information_gain

    def _best_split(self, X, y):
        """
        Finds the best split for a given set of features and labels.

        Args:
            X (np.ndarray): The features.
            y (np.ndarray): The labels.

        Returns:
            tuple: The index of the best feature to split on, the best threshold, and the information gain.
        """
        best_feature_index = None
        best_threshold = None
        best_information_gain = 0

        for feature_index in range(X.shape[1]):
            feature_values = np.unique(X[:, feature_index])
            for threshold in feature_values:
                y_left = y[X[:, feature_index] <= threshold]
                y_right = y[X[:, feature_index] > threshold]
                information_gain = self._information_gain(y, y_left, y_right)

                if information_gain > best_information_gain:
                    best_information_gain = information_gain
                    best_feature_index = feature_index
                    best_threshold = threshold

        return best_feature_index, best_threshold, best_information_gain

    def _build_tree(self, X, y, depth=0):
        """
        Recursively builds the decision tree.

        Args:
            X (np.ndarray): The features.
            y (np.ndarray): The labels.
            depth (int, optional): The current depth of the tree. Defaults to 0.

        Returns:
            dict: The decision tree represented as a nested dictionary.
        """
        n_samples, n_features = X.shape
        n_labels = len(np.unique(y))

        # Stopping criteria
        if (self.max_depth is not None and depth >= self.max_depth) or \
           (n_samples < self.min_samples_split) or \
           (n_labels == 1):
            return {"class": np.bincount(y).argmax()}

        # Find the best split
        best_feature_index, best_threshold, best_information_gain = self._best_split(X, y)

        # If no split improves the information gain, return a leaf node
        if best_information_gain == 0:
            return {"class": np.bincount(y).argmax()}

        # Split the data
        X_left = X[X[:, best_feature_index] <= best_threshold]
        y_left = y[X[:, best_feature_index] <= best_threshold]
        X_right = X[X[:, best_feature_index] > best_threshold]
        y_right = y[X[:, best_feature_index] > best_threshold]

        # Recursively build the left and right subtrees
        left_subtree = self._build_tree(X_left, y_left, depth + 1)
        right_subtree = self._build_tree(X_right, y_right, depth + 1)

        # Create the decision node
        return {
            "feature_index": best_feature_index,
            "threshold": best_threshold,
            "left": left_subtree,
            "right": right_subtree
        }

    def fit(self, X, y):
        """
        Fits the decision tree to the training data.

        Args:
            X (np.ndarray): The features.
            y (np.ndarray): The labels.
        """
        try:
            X = np.array(X)
            y = np.array(y)
        except Exception as e:
            raise ValueError(f"Invalid input data: {e}")

        if X.ndim != 2:
            raise ValueError("X must be a 2D array.")
        if y.ndim != 1:
            raise ValueError("y must be a 1D array.")
        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y must have the same number of samples.")

        self.tree = self._build_tree(X, y)

    def _predict_one(self, x, tree):
        """
        Predicts the class for a single sample.

        Args:
            x (np.ndarray): The features of the sample.
            tree (dict): The decision tree.

        Returns:
            int: The predicted class.
        """
        if "class" in tree:
            return tree["class"]

        feature_index = tree["feature_index"]
        threshold = tree["threshold"]

        if x[feature_index] <= threshold:
            return self._predict_one(x, tree["left"])
        else:
            return self._predict_one(x, tree["right"])

    def predict(self, X):
        """
        Predicts the classes for a set of samples.

        Args:
            X (np.ndarray): The features.

        Returns:
            np.ndarray: The predicted classes.
        """
        try:
            X = np.array(X)
        except Exception as e:
            raise ValueError(f"Invalid input data: {e}")

        if X.ndim != 2:
            raise ValueError("X must be a 2D array.")

        return np.array([self._predict_one(x, self.tree) for x in X])


if __name__ == '__main__':
    # Example Usage with a Real Dataset (Iris Dataset)
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score

    # Load the Iris dataset
    iris = load_iris()
    X, y = iris.data, iris.target

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Create a DecisionTreeClassifier instance
    clf = DecisionTreeClassifier(max_depth=3, min_samples_split=5)

    # Fit the classifier to the training data
    clf.fit(X_train, y_train)

    # Make predictions on the test data
    y_pred = clf.predict(X_test)

    # Calculate the accuracy of the classifier
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy}")