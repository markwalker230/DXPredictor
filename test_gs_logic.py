from src.utils import generate_random_gridsquare, gs_to_latlon
import maidenhead

def test_random_gs():
    for _ in range(100):
        gs = generate_random_gridsquare()
        # Verify length
        assert len(gs) == 6, f"Invalid length: {gs}"
        # Verify it can be converted to lat/lon (validates format)
        lat, lon = gs_to_latlon(gs)
        assert lat is not None and lon is not None, f"Invalid gridsquare generated: {gs}"
    print("✅ 100 random gridsquares generated and validated successfully.")

if __name__ == "__main__":
    test_random_gs()
