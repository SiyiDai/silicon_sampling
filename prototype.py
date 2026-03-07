from data_processing import process_predictions


if __name__ == "__main__":
    input_csv = "data/data_clean_less.csv"
    output_csv = "data/data_clean_less_predictions.csv"
    print(f"Processing predictions for {input_csv} and saving to {output_csv}...")
    process_predictions(input_csv, output_csv, limit=None)
