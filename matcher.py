import pandas as pd
import requests
from sklearn.cluster import KMeans

api_key = "YOUR_CENSUS_API_KEY"

# Set the Census API endpoint and desired dataset
url = "https://api.census.gov/data/2020/acs/acs5"
variables = (
    "NAME,B01001_001E,B01002_001E,B25001_001E,B19013_001E"  # Population, Median Age, Housing Units, Median Income
)


num_states = int(input("Enter the number of states you want to include: "))
states = []
for i in range(num_states):
    state_code = input(f"Enter the state code for state {i + 1}: ")
    states.append(state_code)


zip_url = "https://api.census.gov/data/2020/acs/acs5/variables"
zip_codes = []
for state in states:
    params = {
        "get": "NAME",
        "for": "zip code tabulation area:*",
        "in": f"state:{state}",
        "key": api_key,
    }
    response = requests.get(zip_url, params=params)
    if response.status_code == 200:
        zip_codes.extend([(row[1], row[2]) for row in response.json()[1:]])  # Ignore header row

# Fetch data for the selected zip codes
data = []
for state, zipcode in zip_codes:
    params = {
        "get": variables,
        "for": f"zip code tabulation area:{zipcode}",
        "in": f"state:{state}",
        "key": api_key,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data.extend(response.json()[1:])  # Ignore header row


columns = ["name", "total_population", "median_age", "total_housing_units", "median_income", "state", "zipcode"]
df = pd.DataFrame(data, columns=columns)

# Convert numeric columns to appropriate data types
numeric_columns = ["total_population", "median_age", "total_housing_units", "median_income"]
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Handle missing values
df = df.dropna()

# Normalize data for clustering
normalized_df = (df[numeric_columns] - df[numeric_columns].mean()) / df[numeric_columns].std()

# Perform k-means clustering to create matched markets
n_clusters = 2  # Adjust the number of clusters (markets) as needed
kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(normalized_df)

# Add matched market labels to the original DataFrame
df["matched_market"] = kmeans.labels_

print(df)
