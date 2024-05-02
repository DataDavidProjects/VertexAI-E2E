import pandas as pd
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split

# Generate regression data
n_features = 10
X, y = make_regression(n_samples=5000, n_features=n_features, noise=0.1)

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Split the train set into train and validation sets
X_train, X_val, y_train, y_val = train_test_split(
    X_train, y_train, test_size=0.2, random_state=42
)

# Print the shapes of the datasets
print("Train set shape:", X_train.shape, y_train.shape)
print("Validation set shape:", X_val.shape, y_val.shape)
print("Test set shape:", X_test.shape, y_test.shape)


# Save all  as csv files using names: X_train.csv, X_val.csv, X_test.csv, y_train.csv, y_val.csv, y_test.csv
for name, data in zip(
    ["X_train", "X_val", "X_test", "y_train", "y_val", "y_test"],
    [X_train, X_val, X_test, y_train, y_val, y_test],
):
    columns = (
        [f"feature_{i}" for i in range(1, n_features + 1)]
        if "X" in name
        else ["target"]
    )
    print(columns)
    pd.DataFrame(data, columns=columns).to_csv(name + ".csv", index=False)
    print(name, data.shape)
    # Print Schema for BigQuery
    print(pd.DataFrame(data, columns=columns).dtypes)
