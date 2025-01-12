# create conditioning contexts


def create_context(demographic_data):
    return f"I am a {demographic_data['age']}-year-old {demographic_data['gender']}, interested in {demographic_data['interests']}."
