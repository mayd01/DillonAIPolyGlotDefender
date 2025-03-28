import pickle

with open("/data/processed/preprocessed_data.pkl", "rb") as f:
    data = pickle.load(f)

print(type(data))  # Check if it's a tuple, list, or something else
print(len(data))   # If it's a tuple or list, check its length
