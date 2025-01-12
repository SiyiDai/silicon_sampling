from data_processing import process_personas

# from validation import validate_output


# Generate synthetic data
if __name__ == "__main__":
    input_csv = "data/persona_profiles.csv"  # Replace with your input CSV file
    output_csv = "data/persona_profiles_with_responses.csv"  # Replace with your desired output file name
    process_personas(input_csv, output_csv)
