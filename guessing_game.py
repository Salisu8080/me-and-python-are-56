"""
Develop a Python guessing game that will
randomly pick a number between 1 and 10,
and the user will try to guess it.

🧠 Features:
Uses random to generate a number.
Takes user input.
Gives feedback (too high/low).
Tells the user if they guessed correctly or not.
"""
import random

def guesing_game():
    print("🎲 Welcome to the Number Guessing game")
    number_to_guess = random.randint(1,100)
    attempts = 0
    guessed = False

    while not guessed:
        try:
            
            guess = int(input("Guess a number between 1 and 100:"))
            attempts += 1

            if guess < 1 or guess > 100:
                print("Please guess a number **within** the range!")
                continue
            if guess < number_to_guess:
                print("Too low! Try again.")
            elif guess > number_to_guess:
                print("Too high! Try again")
            else:
                guessed =True
                print(f"🎉Congratulations You guessed it in {attempts} attempts.")
        except ValueError:
            print("⚠️Invalid input. Please enter a number")
#start the game
guesing_game()


