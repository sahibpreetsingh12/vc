import numpy as np
from sklearn.model import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class RandomForest:
    """
    A Random Forest Classifier implemented using scikit-learn.

    Attributes:
        n_estimators (int): The number of trees in the forest.
        model (RandomForestClassifier): The scikit-learn RandomForestClassifier object.
    """

    def __init__(self, n_estimators=5):
        """
        Initializes the RandomForest with the specified number of trees.

        Args:
            n_estimators (int): The number of trees in the forest. Defaults to 5.
        """
        if not isinstance(n_estimators, int) or n_estimators <= 0:
            raise ValueError("n_estimators must be a positive integer.")
        self.n_estimators = n_estimators
        self.model = RandomForestClassifier(n_estimators=self.n_estimators, random_state=42) # Setting random_state for reproducibility

    def fit(self, X, y):
        """
        Fits the Random Forest model to the training data.

        Args:
            X (numpy.ndarray or pandas.DataFrame): The training input samples.
            y (numpy.ndarray or pandas.Series): The target values (class labels).

        Raises:
            ValueError: If X or y are not array-like or if their lengths don't match.
        """
        try:
            X = np.asarray(X)
            y = np.asarray(y)
        except Exception as e:
            raise ValueError(f"Could not convert X or y to numpy arrays. Error: {e}")

        if len(X) != len(y):
            raise ValueError("X and y must have the same length.")

        self.model.fit(X, y)

    def predict(self, X):
        """
        Predicts class labels for the input data.

        Args:
            X (numpy.ndarray or pandas.DataFrame): The input samples.

        Returns:
            numpy.ndarray: The predicted class labels.

        Raises:
            ValueError: If X is not array-like.
        """
        try:
            X = np.asarray(X)
        except Exception as e:
            raise ValueError(f"Could not convert X to a numpy array. Error: {e}")

        return self.model.predict(X)

    def evaluate(self, X, y):
        """
        Evaluates the model's performance using accuracy.

        Args:
            X (numpy.ndarray or pandas.DataFrame): The input samples.
            y (numpy.ndarray or pandas.Series): The true class labels.

        Returns:
            float: The accuracy score.

        Raises:
            ValueError: If X or y are not array-like or if their lengths don't match.
        """
        try:
            X = np.asarray(X)
            y = np.asarray(y)
        except Exception as e:
            raise ValueError(f"Could not convert X or y to numpy arrays. Error: {e}")

        if len(X) != len(y):
            raise ValueError("X and y must have the same length.")

        y_pred = self.predict(X)
        return accuracy_score(y, y_pred)


if __name__ == '__main__':
    # Example Usage
    # Generate some dummy data
    X = np.random.rand(100, 10)  # 100 samples, 10 features
    y = np.random.randint(0, 2, 100)  # Binary classification

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the Random Forest model
    try:
        rf_model = RandomForest(n_estimators=7)
        rf_model.fit(X_train, y_train)

        # Evaluate the model
        accuracy = rf_model.evaluate(X_test, y_test)
        print(f"Accuracy: {accuracy}")

        # Make predictions
        predictions = rf_model.predict(X_test)
        print(f"Predictions: {predictions}")

    except ValueError as e:
        print(f"Error: {e}")