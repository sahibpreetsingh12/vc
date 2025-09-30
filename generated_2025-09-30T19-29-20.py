import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import warnings

def combined_model_example(data_path):
    """
    Demonstrates a combined model using Decision Trees, Random Forest, and XGBoost
    on a practical dataset.  Handles data loading, preprocessing, model training,
    and evaluation.

    Args:
        data_path (str): The path to the CSV file containing the dataset.
                           The dataset should have a categorical target variable.

    Returns:
        None. Prints the accuracy and classification reports for each model.
    """
    try:
        # Load the dataset
        data = pd.read_csv(data_path)

        # Handle missing values (replace with the most frequent value)
        for column in data.columns:
            if data[column].isnull().any():
                data[column] = data[column].fillna(data[column].mode()[0])

        # Identify categorical features
        categorical_features = data.select_dtypes(include=['object']).columns

        # Encode categorical features using Label Encoding
        label_encoders = {}
        for feature in categorical_features:
            label_encoders[feature] = LabelEncoder()
            data[feature] = label_encoders[feature].fit_transform(data[feature])

        # Separate features (X) and target (y)
        X = data.drop('target', axis=1)  # Assuming 'target' is the target column name
        y = data['target']

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # --- Decision Tree Model ---
        dt_model = DecisionTreeClassifier(random_state=42)
        dt_model.fit(X_train, y_train)
        dt_predictions = dt_model.predict(X_test)
        dt_accuracy = accuracy_score(y_test, dt_predictions)
        print("Decision Tree Model:")
        print(f"Accuracy: {dt_accuracy:.4f}")
        print("Classification Report:\n", classification_report(y_test, dt_predictions))

        # --- Random Forest Model ---
        rf_model = RandomForestClassifier(random_state=42)
        rf_model.fit(X_train, y_train)
        rf_predictions = rf_model.predict(X_test)
        rf_accuracy = accuracy_score(y_test, rf_predictions)
        print("\nRandom Forest Model:")
        print(f"Accuracy: {rf_accuracy:.4f}")
        print("Classification Report:\n", classification_report(y_test, rf_predictions))

        # --- XGBoost Model ---
        xgb_model = XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss') # Suppress the warning and set eval_metric
        xgb_model.fit(X_train, y_train)
        xgb_predictions = xgb_model.predict(X_test)
        xgb_accuracy = accuracy_score(y_test, xgb_predictions)
        print("\nXGBoost Model:")
        print(f"Accuracy: {xgb_accuracy:.4f}")
        print("Classification Report:\n", classification_report(y_test, xgb_predictions))

    except FileNotFoundError:
        print(f"Error: The file '{data_path}' was not found.")
    except KeyError:
        print("Error: The 'target' column was not found in the dataset. Please ensure the dataset has a column named 'target'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    # Example usage: Replace 'your_data.csv' with the actual path to your data file.
    # Ensure your data has a 'target' column for classification.  The target
    # column and any other categorical features should be strings or convertible
    # to strings, as they will be processed using LabelEncoder.
    # A sample CSV is created if one doesn't exist.
    try:
        df = pd.read_csv('sample_data.csv')
    except FileNotFoundError:
        data = {'feature1': ['A', 'B', 'A', 'C', 'B'],
                'feature2': [1, 2, 3, 4, 5],
                'feature3': ['X', 'Y', 'X', 'Z', 'Y'],
                'target': ['yes', 'no', 'yes', 'no', 'yes']}
        df = pd.DataFrame(data)
        df.to_csv('sample_data.csv', index=False)

    warnings.filterwarnings("ignore")  # Suppress warnings for cleaner output.  Remove in production if warnings are important.
    combined_model_example('sample_data.csv')