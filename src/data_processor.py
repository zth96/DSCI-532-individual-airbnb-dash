import pandas as pd

def clean_and_process_data(file_path):
    # Load the dataset
    data = pd.read_csv(file_path)

    # Handling missing values
    # Assuming 'name' and 'host_name' can be filled with placeholder text
    data['name'].fillna('No Name Provided', inplace=True)
    data['host_name'].fillna('No Host Name', inplace=True)

    # For 'last_review' and 'reviews_per_month', missing values likely mean no reviews
    data['last_review'].fillna('Not Reviewed', inplace=True)
    data['reviews_per_month'].fillna(0, inplace=True)

    # Handling potential outliers
    # Assuming prices above a certain threshold (e.g., $1000 per night) are outliers
    max_price_threshold = 1000
    data = data[data['price'] <= max_price_threshold]

    # Handling extreme values in 'minimum_nights'
    max_minimum_nights = 365  # setting a sensible maximum
    data = data[data['minimum_nights'] <= max_minimum_nights]

    # Ensure correct data types
    data['last_review'] = pd.to_datetime(data['last_review'], errors='coerce')  # Convert to datetime

    return data

def save_processed_data(data, output_path):
    data.to_csv(output_path, index=False)

if __name__ == "__main__":
    # Example usage
    file_path = 'data/raw/AB_NYC_2019.csv'
    processed_data = clean_and_process_data(file_path)
    save_processed_data(processed_data, 'data/processed/processed_data.csv')
