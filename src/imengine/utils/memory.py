'''
A data structure to track global memory of all Agents within a Graph. Stores each prompt/response as JSON objects, able to be queried upon and filtered.
'''

from __future__ import annotations
from utils.start_end import END

class Memory:
    def __init__(self):
        self.memory = []

    def add(self, author: Agent, recipient: Agent, content: str):
        if recipient is END:
            recipient.name = 'END'
        new = {
            'author': author.name,
            'recipient': recipient.name,
            'content': content
        }
        self.memory.append(new)
    
    def get(self, author: list['Agent'], recipient: list['Agent']):
        return [m for m in self.memory if m['author'] in author and m['recipient'] in recipient]
    
    def get_formatted(self, author: list['Agent'], recipient: list['Agent']):
        '''
        
        '''
        return '\n'.join([f"{m['author']} -> {m['recipient']}: {m['content']}" for m in self.memory if m['author'] in [a.name for a in author] and m['recipient'] in [a.name for a in recipient]])

    def get_all(self):
        return self.memory

    def clear(self):
        self.memory = []

    def __str__(self):
        return str(self.memory)

    def __repr__(self):
        return str(self.memory)