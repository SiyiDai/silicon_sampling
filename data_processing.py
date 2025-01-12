import pandas as pd
from data_generation import generate_response
from context_generation import generate_persona_data


def process_personas(input_csv, output_csv):
    """
    Process all personas and save the responses into a table.

    Args:
        input_csv (str): Path to the input CSV file with persona contexts.
        output_csv (str): Path to the output CSV file to save responses.
    """
    # Load the persona data and generate the context
    # data = pd.read_csv(input_csv)
    data = generate_persona_data(input_csv)

    # Add new columns for the response components
    data["Shopping Preference"] = ""
    data["Price Range (€)"] = ""
    data["Lamps per Year"] = ""
    data["Valued Aspects"] = ""

    # Iterate through each persona context and generate a response
    for index, row in data.iterrows():
        context = row["Conditioning Context"]
        response = generate_response(context)

        # Parse the response into individual components
        response_parts = [part.strip() for part in response.split(",")]
        data.at[index, "Shopping Preference"] = response_parts[0]
        data.at[index, "Price Range (€)"] = response_parts[1]
        data.at[index, "Lamps per Year"] = response_parts[2]
        data.at[index, "Valued Aspects"] = response_parts[3]

    # Save the updated DataFrame to the output CSV
    data.to_csv(output_csv, index=False)
    print(f"Responses saved to {output_csv}")
