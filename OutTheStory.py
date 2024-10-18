import streamlit as st
import random

# List of categories and their respective items (10 words per category)
categories = {
    "Football Players": ["Messi", "Ronaldo", "Mbappe", "Neymar", "Salah", "Lewandowski", "Benzema", "Kane", "Haaland", "Modric"],
    "Animals": ["Dog", "Cat", "Elephant", "Lion", "Tiger", "Horse", "Giraffe", "Kangaroo", "Panda", "Dolphin"],
    "Clothes": ["Shirt", "Pants", "Hat", "Jacket", "Socks", "Scarf", "Sweater", "Shoes", "Belt", "Gloves"],
    "Fruits": ["Apple", "Banana", "Orange", "Strawberry", "Grape", "Mango", "Pineapple", "Cherry", "Peach", "Watermelon"]
}

# Initialize session state to store the game state
if 'step' not in st.session_state:
    st.session_state.step = 'setup'
    st.session_state.players = []
    st.session_state.imposter = None
    st.session_state.detective = None
    st.session_state.silencer = None
    st.session_state.current_player_index = 0
    st.session_state.category = None
    st.session_state.word_for_in_players = None
    st.session_state.asked_players = []
    st.session_state.answered_players = []
    st.session_state.word_choices = []
    st.session_state.scores = {}  # To track scores of players and imposter
    st.session_state.show_guide = True  # Flag for showing guide
    st.session_state.event_active = False  # To track if the event is enabled
    st.session_state.double_points_this_round = False  # Track if double points is active for the current round
    st.session_state.game_mode = None  # Track if we are in classic or advanced mode

# Sidebar for setup
with st.sidebar:
    st.title("Setup")
    
    # Select game mode (Classic or Advanced)
    st.session_state.game_mode = st.selectbox("Choose Game Mode", ["Classic", "Advanced"])
    
    # Select category
    st.session_state.category = st.selectbox("Choose a category", list(categories.keys()))
    
    # Get number of players
    num_players = st.number_input('Enter the number of players', min_value=3, max_value=10, step=1)

    # Collect players' names
    players = []
    for i in range(num_players):
        player_name = st.text_input(f'Enter name for player {i+1}', key=f'player_{i}')
        if player_name:
            players.append(player_name)

    # Event Activation Checkbox
    st.session_state.event_active = st.checkbox("Activate Event? (20% chance of Double Points)")

    # Button to start the game
    if st.button('Start Game') and len(players) == num_players:
        st.session_state.players = players
        st.session_state.imposter = random.choice(players)
        st.session_state.word_for_in_players = random.choice(categories[st.session_state.category])

        if st.session_state.game_mode == "Advanced":
            # Assign a Detective and a Silencer randomly (different from imposter)
            roles_players = [p for p in players if p != st.session_state.imposter]
            st.session_state.detective = random.choice(roles_players)
            roles_players.remove(st.session_state.detective)
            st.session_state.silencer = random.choice(roles_players)

        # Initialize scores
        for player in players:
            st.session_state.scores[player] = 0
        st.session_state.scores[st.session_state.imposter] = 0  # Imposter's score initialization
        
        st.session_state.step = 'reveal'
        st.session_state.current_player_index = 0
        st.session_state.show_guide = False  # Hide the guide

# Main content area
st.title("برا القصة - Out of the Story")

# Game Guide
if st.session_state.show_guide:
    with st.expander("Game Guide", expanded=True):
        st.write("""
        Welcome to the game! Here’s how to play:

        1. **Setup**: Enter the number of players (minimum 3) and their names. Choose a category for the words.
        2. **Reveal**: Each player will take turns to reveal if they are "IN" or "OUT" of the story. The imposter will be selected randomly.
        3. **Questioning Phase**: Players will ask questions to each other to find out who the imposter is. 
        4. **Guessing Phase**: After questioning, players will guess who they think the imposter is.
        5. **Imposter Guessing**: The imposter will then guess the word that the other players know from a set of choices.
        6. **Scoring**: Players earn points for correctly guessing the imposter, and the imposter earns points for guessing the correct word.

        If the **Event** is active, there will be a 20% chance to double points for this round!

        In **Advanced Mode**, two additional roles are introduced:
        - **Detective**: Tries to uncover the imposter.
        - **Silencer**: Must avoid revealing their identity while assisting the imposter.

        Have fun and may the best player win!
        
        Game By Haider
        """)

if st.session_state.step == 'reveal':
    player = st.session_state.players[st.session_state.current_player_index]

    st.write(f"Give the phone to {player} to see if they are in or out of the story.")

    if st.button(f"{player}, Click to Reveal"):
        if player == st.session_state.imposter:
            st.error(f"{player}, you are OUT of the story!")
        else:
            st.success(f"{player}, you are IN the story! Your word is: {st.session_state.word_for_in_players}")
        
        if st.session_state.game_mode == "Advanced":
            if player == st.session_state.detective:
                st.info(f"{player}, you are the **Detective**!")
            elif player == st.session_state.silencer:
                st.warning(f"{player}, you are the **Silencer**!")

        if st.session_state.current_player_index < len(st.session_state.players) - 1:
            st.session_state.current_player_index += 1
        else:
            # Event Trigger: 20% chance for double points if the event is active
            if st.session_state.event_active:
                st.session_state.double_points_this_round = random.random() < 0.2
                if st.session_state.double_points_this_round:
                    st.warning("Double Points Event Activated! Points will be doubled this round!")
                else:
                    st.info("No event this round.")
            else:
                st.session_state.double_points_this_round = False
            
            st.session_state.step = 'Questioning'
            st.session_state.current_player_index = 0

if st.session_state.step == 'Questioning':
    st.write("Questioning Phase: Try to find the imposter!")

    current_asker = st.session_state.players[st.session_state.current_player_index]

    available_answerers = [p for p in st.session_state.players if p != current_asker and p not in st.session_state.answered_players]
    if not available_answerers:
        available_answerers = [p for p in st.session_state.players if p != current_asker]

    selected_answerer = random.choice(available_answerers)

    st.write(f"{current_asker} is asking {selected_answerer}. Ask your question out loud!")

    st.session_state.asked_players.append(current_asker)
    st.session_state.answered_players.append(selected_answerer)

    if st.button("Next Question"):
        if st.session_state.current_player_index < len(st.session_state.players) - 1:
            st.session_state.current_player_index += 1
        else:
            if len(set(st.session_state.asked_players)) < len(st.session_state.players):
                st.session_state.current_player_index = 0
            else:
                st.session_state.step = 'guess_imposter'
                st.session_state.current_player_index = 0

if st.session_state.step == 'guess_imposter':
    st.write("Now it's time to guess the imposter!")

    guesses = []
    for player in st.session_state.players:
        guess = st.selectbox(f"{player}, who do you think is the imposter?", st.session_state.players, key=f'guess_{player}')
        guesses.append((player, guess))

    if st.button('Submit Guesses'):
        for player, guess in guesses:
            if guess == st.session_state.imposter:
                points = 100
                if st.session_state.double_points_this_round:
                    points *= 2  # Double the points if the event triggers
                st.session_state.scores[player] += points

        st.write(f"The imposter was: {st.session_state.imposter}!")
        st.session_state.step = 'imposter_guess'

if st.session_state.step == 'imposter_guess':
    st.write(f"{st.session_state.imposter}, now it's your turn to guess the word!")

    if not st.session_state.word_choices:
        other_words = [word for word in categories[st.session_state.category] if word != st.session_state.word_for_in_players]
        wrong_choices = random.sample(other_words, 7)
        st.session_state.word_choices = [st.session_state.word_for_in_players] + wrong_choices
        random.shuffle(st.session_state.word_choices)

    imposter_guess = st.selectbox(f"Which word do you think is the correct one?", st.session_state.word_choices)

    if st.button("Submit Imposter Guess"):
        if imposter_guess == st.session_state.word_for_in_players:
            st.success("Correct! The imposter guessed the right word.")
            points = 100
            if st.session_state.double_points_this_round:
                points *= 2  # Double points event for imposter as well
            st.session_state.scores[st.session_state.imposter] += points
        else:
            st.error("Incorrect guess. The imposter failed.")

        st.write("Final Scores:")
        for player, score in st.session_state.scores.items():
            st.write(f"{player}: {score} points")

        st.session_state.step = 'end'

if st.session_state.step == 'end':
    st.write("Game Over! Thanks for playing.")
    
