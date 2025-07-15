import json
import pandas as pd

# Load original Json file
with open('data.json', 'r') as f:
    original_json = json.load(f)

# Load altered Json file
with open('altered_data.json', 'r') as f:
    altered_json = json.load(f)

# Convert JSON to DataFrame
def json_to_df(data):
    return pd.DataFrame([
        {
            "user_id": user["user_id"],
            "RiskFactorID": item["RiskFactorID"],
            "updated_by": user.get("updated_by")
        }
        for user in data
        for item in user.get("factor_mapping", [])
    ])

df_original = json_to_df(original_json)
df_altered = json_to_df(altered_json)

# Creating a map from user_id to updated_by from the altered Json
updated_by_map = {
    user["user_id"]: user.get("updated_by")
    for user in altered_json
}

# Find removed RiskFactorIDs (in original but not in altered)
removed = pd.merge(df_original, df_altered, on=["user_id", "RiskFactorID"], how='left', indicator=True)
removed = removed[removed['_merge'] == 'left_only'][["user_id", "RiskFactorID"]]
removed["Type"] = "REMOVED"
removed["updated_by"] = removed["user_id"].map(updated_by_map)

# Find added RiskFactorIDs (in altered but not in original)
added = pd.merge(df_altered, df_original, on=["user_id", "RiskFactorID"], how='left', indicator=True)
added = added[added['_merge'] == 'left_only'][["user_id", "RiskFactorID"]]
added["Type"] = "ADDED"
added["updated_by"] = added["user_id"].map(updated_by_map)

# Combine both
df_diff = pd.concat([removed, added], ignore_index=True)[["user_id", "RiskFactorID", "updated_by", "Type"]]

# Output
if df_diff.empty:
    print("\nNo differences detected between original and altered JSON.")
else:
    print("\n=== Differences Detected ===")
    print(df_diff)

# Save to CSV
df_diff.to_csv("factor_differences.csv", index=False)
print("\nDifferences saved to 'factor_differences.csv'")
