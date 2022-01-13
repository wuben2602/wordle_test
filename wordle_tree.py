from dataclasses import dataclass
from string import ascii_lowercase
from enum import Enum 

import json

class WordType(Enum):
    ROOT = 0
    GREEN = 1
    YELLOW = 2
    GRAY = 3
    
@dataclass
class WordleNode:
        
    name : str # depth_letter_type
    value : int # init to 1
    children : dict # empty dict
    type : WordType # init
    
    ''' adds node to tree; if node already exists, increments value of it '''
    def add_node(self, name : str, type : WordType):
        if name in self.children:
            self.children[name].value += 1
        else:
            node = WordleNode(name, 1, dict(), type)
            self.children[name] = node
        
class WordleTree:
    
    root : WordleNode
    words : dict
    count : int
    
    def __init__(self, doc : str = "words.json"):
        self.root = WordleNode("0_root_ROOT", 0, dict(), WordType.ROOT)
        with open(doc) as txt:
            self.words = json.load(txt)["solutions"]
        self.__grow_tree()
        
    def __grow_tree(self):
        
        # depth_letter --> every other word grows tree from root up
        for word1 in self.words:
            for word2 in self.words:
                if word1 == word2:
                    break
                curr_node = self.root # start from root to traverse
                curr_word = list(word1)
                comp_word = list(word2)
                
                for i in range(5): # fill out branches
                    depth = i + 1
                    if curr_word[i] == comp_word[i]: # green
                        letter_type = WordType.GREEN
                    elif curr_word[i] in word2: # yellow
                        letter_type = WordType.YELLOW
                    else:
                        letter_type = WordType.GRAY
                    name = f'{depth}_{curr_word[i]}_{letter_type.name}'
                    curr_node.add_node(name, letter_type)
                    curr_node = curr_node.children[name]              
    
    def to_string(self, curr_node : WordleNode = None, indent : int = 0):
        if not curr_node:
            curr_node = self.root
        print('.'*indent + f"{curr_node.name} : {curr_node.value}")
        if not curr_node.children:
            return
        else:
            for child in curr_node.children.keys(): 
                self.to_string(curr_node.children[child], indent + 1)
                                 
if __name__ == "__main__":
    tree = WordleTree("words1.json")
    tree.to_string()