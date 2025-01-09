import cv2
import mediapipe as mp
import random

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Function to classify hand gestures (Rock, Paper, Scissors, Victory Sign, etc.)
def hand_gesture(landmarks):
    thumb_tip = landmarks[4].y
    index_tip = landmarks[8].y
    middle_tip = landmarks[12].y
    ring_tip = landmarks[16].y
    pinky_tip = landmarks[20].y
    knuckle_1 = landmarks[5].y
    knuckle_2 = landmarks[9].y
    knuckle_3 = landmarks[13].y
    knuckle_4 = landmarks[17].y

    # Paper: All fingers extended
    if index_tip < knuckle_1 and middle_tip < knuckle_2 and ring_tip < knuckle_3 and pinky_tip < knuckle_4:
        return "Paper"
    # Scissors: Index and middle fingers extended
    elif index_tip < knuckle_1 and middle_tip < knuckle_2 and ring_tip > knuckle_3 and pinky_tip > knuckle_4:
        return "Scissors"
    # Rock: All fingers curled
    elif index_tip > knuckle_1 and middle_tip > knuckle_2 and ring_tip > knuckle_3 and pinky_tip > knuckle_4:
        return "Rock"
    # I Love You: Thumb, index, and pinky extended, middle and ring curled
    elif thumb_tip < index_tip and index_tip < knuckle_1 and pinky_tip < knuckle_4 and middle_tip > knuckle_2 and ring_tip > knuckle_3:
        return "I Love You"
    # Victory Sign (V sign): Index and middle fingers extended, others curled
    elif index_tip < knuckle_1 and middle_tip < knuckle_2 and ring_tip > knuckle_3 and pinky_tip > knuckle_4:
        return "Victory"
    else:
        return "Unknown"

# Function to determine the winner
def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return "It's a Tie!", 0
    elif (user_choice == "Rock" and computer_choice == "Scissors") or \
         (user_choice == "Paper" and computer_choice == "Rock") or \
         (user_choice == "Scissors" and computer_choice == "Paper"):
        return "You Win!", 1
    else:
        return "Computer Wins!", -1

# Function to list available cameras
def list_cameras():
    index = 0
    available_cameras = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            available_cameras.append(index)
        cap.release()
        index += 1
    return available_cameras

# Choose camera source
print("Available Cameras:")
cameras = list_cameras()
for i, cam in enumerate(cameras):
    print(f"{i}: Camera {cam}")

# Wait for user to input camera index
camera_choice = int(input("Select the camera source by entering the corresponding number: "))
cap = cv2.VideoCapture(cameras[camera_choice])

# Game state variables
last_user_choice = "None"
computer_choice = random.choice(["Rock", "Paper", "Scissors"])
result_text = "Make a gesture!"
user_score = 0
computer_score = 0

# Main loop to process video feed
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame for a mirror effect
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process hand landmarks
    result = hands.process(rgb_frame)

    # Check for "I Love You" gesture to quit the game
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            user_choice = hand_gesture(hand_landmarks.landmark)
            if user_choice == "I Love You":
                cv2.putText(frame, "Game Over! I Love You Gesture Detected!", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow("Rock Paper Scissors", frame)
                cv2.waitKey(3000)  # Pause for 3 seconds before quitting
                cap.release()
                cv2.destroyAllWindows()
                exit()

    # Default user choice
    user_choice = "None"

    # If hand landmarks are detected
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Only draw hand landmarks and connections if you want to visualize them
            # If you want to disable drawing lines or dots (balloons), comment out the line below
            # mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            user_choice = hand_gesture(hand_landmarks.landmark)

    # Only update computer's choice and result if a valid user gesture is made
    if user_choice != "None" and user_choice != "Unknown" and user_choice != last_user_choice:
        last_user_choice = user_choice
        computer_choice = random.choice(["Rock", "Paper", "Scissors"])
        result_text, score_change = determine_winner(user_choice, computer_choice)

        # Update scores
        if score_change == 1:
            user_score += 1
        elif score_change == -1:
            computer_score += 1

    # Display the user's choice, computer's choice, result, and scores
    cv2.putText(frame, f"Your Choice: {last_user_choice}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Computer: {computer_choice}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Result: {result_text}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(frame, f"Score: You {user_score} - {computer_score} Computer", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Show the frame
    cv2.imshow("Rock Paper Scissors", frame)

    # Check for game over condition (best of 5)
    if user_score == 5 or computer_score == 5:
        winner = "You" if user_score > computer_score else "Computer"
        cv2.putText(frame, f"Game Over! {winner} Wins!", (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Rock Paper Scissors", frame)
        cv2.waitKey(3000)  # Pause for 3 seconds before resetting
        user_score = 0
        computer_score = 0

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
