import threading
import time

def start_vote_timer(blockchain, duration_seconds=300):
    def close_vote():
        print(f"The votes will close in {duration_seconds} seconds")
        time.sleep(duration_seconds)
        blockchain.vote_closed = True
        print("Votes Closed!")

    timer_thread = threading.Thread(target=close_vote, daemon=True)
    timer_thread.start()
