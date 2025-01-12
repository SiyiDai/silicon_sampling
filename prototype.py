from context_generation import create_context
from data_generation import generate_response

# from validation import validate_output

# Load demographic data
demographic_data = {"age": 28, "gender": "female", "interests": "sustainability"}

# Generate context
context = create_context(demographic_data)

# Generate synthetic data
synthetic_response = generate_response(context)

# Validate response
print("Synthetic Response:", synthetic_response)
