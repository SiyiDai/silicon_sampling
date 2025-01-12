import pandas as pd


def generate_persona_data(csv_file):
    """
    Load a CSV file and generate conditioning contexts for each persona.

    Args:
        csv_file (str): Path to the CSV file containing persona profiles.

    Returns:
        pd.DataFrame: DataFrame with a new 'Conditioning Context' column.
    """
    # Load the CSV data into a pandas DataFrame
    data = pd.read_csv(csv_file)

    # Define a function to create conditioning contexts
    def create_context(row):
        return (
            f"I am a {row['Age']}-year-old {row['Cultural Background']} {row['Sex']}, "
            f"with a monthly disposable income of €{row['Income Level (€)']}. "
            f"I live in a {row['Living Conditions']} and spend approximately €{row['Grocery Expense (€)']} on groceries each month. "
            f"My brand perception is '{row['Brand Perception']}'."
        )

    # Generate conditioning contexts for all rows in the DataFrame
    data["Conditioning Context"] = data.apply(create_context, axis=1)

    # # Display the first few rows with the generated contexts
    # print(data[["Name", "Conditioning Context"]])

    # Optional: Save the updated DataFrame with conditioning contexts to a new CSV file
    # output_file = "college_student_personas_with_context.csv"
    # data.to_csv(output_file, index=False)

    return data


# generate_persona_data("persona_profiles.csv")
