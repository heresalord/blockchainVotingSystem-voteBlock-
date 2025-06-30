import datetime
import hashlib
import json
import time
from threading import Lock


class Block:
    def __init__(self, index, timestamp, npi, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.npi = npi
        self.data = data
        self.previous_hash = previous_hash
        self.proof = 0
        self.hash = self.calculate_hash()
        self.hash_attempts = 0
        self.hash_rate = 0

    def calculate_hash(self):
        hash_string = (
            str(self.index)
            + str(self.timestamp)
            + str(self.npi)
            + str(self.data)
            + str(self.previous_hash)
            + str(self.proof)
        )
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        start_time = time.time()
        while self.hash[:difficulty] != "0" * difficulty:
            self.proof += 1
            self.hash = self.calculate_hash()
            self.hash_attempts += 1

        end_time = time.time()
        duration = end_time - start_time
        self.hash_rate = self.hash_attempts / duration if duration > 0 else 0
        print(f"Block mined in {duration:.2f} seconds with hash rate: {self.hash_rate:.2f} hashes/second")
        return self.hash_rate

    def __str__(self):
        return json.dumps({
            "index": self.index,
            "timestamp": self.timestamp.isoformat(),
            "npi": self.npi,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "proof": self.proof,
            "hash": self.hash,
            "hash_attempts": self.hash_attempts,
            "hash_rate": self.hash_rate
        }, indent=4)


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4
        self.voters = set()
        self.vote_closed = False
        self.lock = Lock()

    def create_genesis_block(self):
        return Block(0, datetime.datetime.now(), "", "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        with self.lock:
            new_block.previous_hash = self.get_latest_block().hash
            new_block.mine_block(self.difficulty)
            self.chain.append(new_block)
            print("New block added to the blockchain:", new_block)

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def record_vote(self, full_name, npi, choice):
        with self.lock:
            if self.vote_closed:
                return "The vote is closed!"
            if npi in self.voters:
                return "Your vote has already been recorded!"
            if choice not in ["Paul", "Pierre"]:
                return "Invalid choice!"
            self.voters.add(npi)
            block = Block(len(self.chain), datetime.datetime.now(), npi, f"Voter: {full_name}, Voted for: {choice}", "")
            self.add_block(block)
            return block.hash

    def get_block_by_hash(self, hash_value):
        for block in self.chain:
            if block.hash == hash_value:
                return block
        return None

    def get_winner(self):
        candidate_votes = {"Paul": 0, "Pierre": 0}
        for block in self.chain[1:]:
            if "Paul" in block.data:
                candidate_votes["Paul"] += 1
            elif "Pierre" in block.data:
                candidate_votes["Pierre"] += 1

        if candidate_votes["Paul"] == candidate_votes["Pierre"]:
            return "No one because of a tie"
        else:
            return max(candidate_votes, key=candidate_votes.get)

    def get_average_hash_rate(self):
        total_hash_rate = sum(block.hash_rate for block in self.chain[1:])
        num_blocks = len(self.chain) - 1
        return total_hash_rate / num_blocks if num_blocks > 0 else 0
