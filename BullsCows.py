# Importing Necessary Libraries
import streamlit as st
import random
import math
from itertools import permutations


# Function to generate a secret 4-digit number with unique digits
def generate_secret():
    return random.sample(range(10), 4)


# Function to generate all possible valid 4-digit numbers (no repeated digits)
def all_possible_states():
    return list(permutations(range(10), 4))


# Function to calculate Shannon entropy based on the remaining possible states
def calculate_entropy(possible_states):
    total = len(possible_states)
    if total == 0:  # Handle edge case where no states remain
        return 0
    probabilities = [1 / total] * total
    return -sum(p * math.log2(p) for p in probabilities)


# Function to evaluate the player's guess and provide feedback (Bulls and Cows)
def evaluate_guess(secret, guess):
    # Calculate Bulls (correct digit in the correct position)
    bulls = sum(s == g for s, g in zip(secret, guess))
    # Calculate Cows (correct digit in the wrong position)
    cows = sum((secret.count(g) for g in guess)) - bulls
    return bulls, cows


# Function to filter possible states based on feedback from the current guess
def filter_possible_states(possible_states, guess, bulls, cows):
    # Helper function to check if a state matches the feedback
    def feedback_matches(state):
        state_bulls = sum(s == g for s, g in zip(state, guess))
        state_cows = sum((state.count(g) for g in guess)) - state_bulls
        return state_bulls == bulls and state_cows == cows

    # Filter the states that match the feedback
    return [state for state in possible_states if feedback_matches(state)]


# Function to reset the game state variables and restart the game
def restart_game():
    st.session_state.secret = generate_secret()  # Generate a new secret number
    st.session_state.guesses = []  # Reset list of guesses
    st.session_state.entropies = []  # Reset entropy values
    st.session_state.game_over = False  # Reset game-over status
    st.session_state.possible_states = all_possible_states()  # Reset possible states


# Function to set the background color of the Streamlit page to black
def set_background_color():
    st.markdown(
        """
        <style>
        body {
            background-color: black;  /* Set background color */
            color: white;  /* Set text color */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Main function to run the Streamlit application
def main():
    set_background_color()  # Set custom background color

    # Ensure all required session state variables are initialized
    if "secret" not in st.session_state:
        st.session_state.secret = generate_secret()
    if "guesses" not in st.session_state:
        st.session_state.guesses = []
    if "entropies" not in st.session_state:
        st.session_state.entropies = []
    if "game_over" not in st.session_state:
        st.session_state.game_over = False
    if "possible_states" not in st.session_state:
        st.session_state.possible_states = all_possible_states()

    # Title and introductory instructions
    st.title("Bulls and Cows Game with Entropy")
    st.write(
        "Welcome to the Bulls and Cows game! Can you guess the secret 4-digit number?"
    )
    st.write("### Instructions:")
    st.markdown(
        """
    - The secret number has 4 digits, each unique.
    - Enter your guesses below.
    - You will receive feedback:
      - **Bulls**: Correct digit in the correct position.
      - **Cows**: Correct digit in the wrong position.
    - The current entropy will indicate the remaining uncertainty.
    """
    )

    # Add a Restart Game button
    if st.button("Restart Game"):
        restart_game()  # Reset the game state
        st.success("Game has been restarted!")  # Notify the user

    # Game logic and feedback loop
    if not st.session_state.game_over:
        # Input field for the player's guess
        guess_input = st.text_input("Enter your guess (4 unique digits):", "")
        if st.button("Submit Guess"):
            try:
                # Parse the input into a list of integers
                guess = list(map(int, guess_input))
                if len(guess) != 4 or len(set(guess)) != 4:  # Validate input
                    st.error("Invalid guess. Please enter 4 unique digits.")
                else:
                    # Evaluate the guess and provide feedback
                    bulls, cows = evaluate_guess(st.session_state.secret, guess)
                    st.session_state.guesses.append((guess, bulls, cows))

                    # Update possible states and calculate entropy
                    st.session_state.possible_states = filter_possible_states(
                        st.session_state.possible_states, guess, bulls, cows
                    )
                    entropy = calculate_entropy(st.session_state.possible_states)
                    st.session_state.entropies.append(entropy)

                    # Display feedback to the player
                    st.success(f"Guess: {guess} | Bulls: {bulls}, Cows: {cows}")
                    st.info(f"Current Entropy: {entropy:.4f}")

                    # Check if the player has guessed the number correctly
                    if bulls == 4:
                        st.balloons()  # Celebrate the victory
                        st.success("Congratulations! You guessed the number!")
                        st.write(f"Secret number: {st.session_state.secret}")
                        st.write(f"Total guesses: {len(st.session_state.guesses)}")
                        st.subheader("Your Entropy Chart looks like :")
                        st.line_chart(st.session_state.entropies)  # Show entropy chart
                        st.session_state.game_over = True  # End the game
            except ValueError:
                st.error("Please enter valid digits.")  # Handle invalid input
    else:
        # Notify the user if the game is over
        st.warning("Game over! Click 'Restart Game' to play again.")


# Run the application
if __name__ == "__main__":
    main()
