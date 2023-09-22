import hashlib

class Stages:
    un_initialized, stage_1, stage_2, stage_3, stage_4 = range(5)

class Status:
    accepted, declined = range(2)

class Progress:
    completed, processing = range(2)

class Block:
    def __init__(self, requester_id, responder_id):
        self.requester_id = requester_id
        self.responder_id = responder_id
        self.block_id = 25  # You may want to set this differently
        self.debt = 0
        self.current_stage = Stages.un_initialized
        self.block_data = ""
        self.blocks_progress = Progress.processing

    def get_block_data(self):
        return self.block_data

    def get_blocks_progress(self):
        return self.blocks_progress

    def initiate_stage_1(self, product, quantity):
        if self.current_stage != Stages.un_initialized:
            return False
        self.block_data += f"stage-1 : {{ {self.requester_id} (requested to) : {self.responder_id} for {product} X {quantity} }}\n"
        self.current_stage = Stages.stage_1
        return True

    def initiate_stage_2(self, response, amount):
        if not response:
            self.block_data += f"stage-2 : {{ {self.responder_id} (canceled the order from) : {self.requester_id} }}\n"
            self.blocks_progress = Progress.completed
            return False
        if self.current_stage != Stages.stage_1:
            return False
        self.block_data += f"stage-2 : {{ {self.responder_id} (responded to) : {self.requester_id} with cost : {amount} }}\n"
        self.current_stage = Stages.stage_2
        return True

    def initiate_stage_3(self, response):
        if response == Status.declined:
            self.block_data += f"stage-3 : {{ {self.requester_id} declined the response from {self.responder_id} }}\n"
            self.blocks_progress = Progress.completed
            return False
        if self.current_stage != Stages.stage_2:
            return False
        self.debt -= self.calculate_debt()
        self.block_data += f"stage-3 : {{ {self.requester_id} accepted the response from {self.responder_id} They were charged with debt of {self.debt} }}\n"
        self.current_stage = Stages.stage_3
        return True

    def initiate_stage_4(self, response_from_requester, response_from_responder):
        if self.current_stage != Stages.stage_3:
            return False
        if not (response_from_requester and response_from_responder):
            if not response_from_requester and not response_from_responder:
                self.block_data += "stage-4 : { Requester and Responder not received their Goods} \n"
            elif not response_from_requester:
                self.block_data += "stage-4 : { Responder received his Goods but Requester not received his Goods } \n"
            else:
                self.block_data += "stage-4 : { Requester received his Goods but Responder not received his Goods } \n"
            self.blocks_progress = Progress.completed
            return False
        self.block_data += "stage-4 : { Requester and Responder received their Goods and the Debt was removed} \n"
        self.debt += self.calculate_debt()
        self.current_stage = Stages.stage_4
        self.blocks_progress = Progress.completed
        return True

    def calculate_debt(self):
        # Implement your debt calculation logic here
        return 0  # Placeholder

class HashBlock:
    def __init__(self, previous_hash_value, current_block):
        self.previous_hash_value = previous_hash_value
        self.current_block = current_block

    def next_hash(self):
        return hashlib.sha256((self.previous_hash_value + self.current_block.get_block_data()).encode()).hexdigest()

    def get_blocks_progress(self):
        return self.current_block.get_blocks_progress()

class BlockList:
    def __init__(self):
        self.previous_hash_value = "0000000000000000"
        self.blocks = []

    def push_back(self, hash_block):
        if self.get_blocks_progress() == Progress.processing:
            return False
        self.blocks.append(hash_block)
        self.previous_hash_value = self.next_hash()
        return True

    def get_blocks_progress(self):
        for block in self.blocks:
            if block.get_blocks_progress() == Progress.processing:
                return Progress.processing
        return Progress.completed

    def next_hash(self):
        return hashlib.sha256(self.previous_hash_value.encode()).hexdigest()

block1 = Block("A", "B")
block1.initiate_stage_1("ProductX", 5)
block1.initiate_stage_2(True, 100)
block1.initiate_stage_3(Status.accepted)
block1.initiate_stage_4(True, True)

hash_block1 = HashBlock("0000000000000000", block1)
block_list = BlockList()
block_list.push_back(hash_block1)
