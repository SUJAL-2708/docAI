from backend.core.classifier import process_classification


def test_hybrid_classification():

    filename = "Engineering_Mathematics_Notes.pdf"

    extracted_text = """
    Semiconductor Physics

    A semiconductor is a material whose electrical
    conductivity lies between conductors and insulators.

    A PN junction is formed by joining P-type and
    N-type semiconductor materials.

    Energy bands and forbidden energy gaps are important
    concepts in semiconductor physics.
    """

    try:

        result = process_classification(
            filename=filename,
            extracted_text=extracted_text
        )

        print("\nCLASSIFICATION RESULT")
        print("=" * 45)

        for key, value in result["classification"].items():

            print(f"{key}: {value}")

        print("\nFINAL DECISION")
        print("=" * 45)

        for key, value in result["decision"].items():

            print(f"{key}: {value}")

    except Exception as error:

        print("Classification failed:", error)


if __name__ == "__main__":

    test_hybrid_classification()