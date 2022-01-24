import re
import random
import pandas

class Wordle:
    
    def __init__(self, txt: str):
        self.frequency_list = [dict(),dict(),dict(),dict(),dict()]
        self.regex = "....."
        
        self.blacklist = list()
        self.greenlist = list()
        self.yellowlist = [[],[],[],[],[]]
        self.guesses = dict()
        
        ### initialize
        with open(txt, "r") as words:
            self.words = {line.strip(): 0 for line in words}
            words.seek(0)
            self.original = {line.strip(): 0 for line in words}
        self.__update_frequency_list(self.words, self.frequency_list)
        self.__grade_words()

    def __update_frequency_list(self, dictionary : dict, frequency_list : list):
        [dictionary.clear() for dictionary in frequency_list]
        for word in dictionary.keys():
            chars = list(word)
            for i in range(5):
                frequency_list[i][chars[i]] = self.frequency_list[i].get(chars[i], 0) + 1

    def __update_words_list(self):

        # list of possible words
        words_list = dict()
        for word in list(self.words.keys()):
            if (re.search(self.regex, word)):
                words_list[word] = 0
        self.words = words_list

        # list of possible words from new
        guesses_list = dict()
        for word in list(self.original.keys()):
            guesses_list[word] = 0
        self.guesses = guesses_list
        
    def update(self, guess: str, sequence: str):
        lookahead = ""
        match = [".", ".", ".", ".", "."]
        for i in range(5):
            symbol = sequence[i]
            letter = guess[i]

            if symbol == "?":
                if letter not in self.yellowlist[i]: self.yellowlist[i].append(letter)
                lookahead += f"(?=\w*{letter})"
                match[i] = f"(?![{''.join(self.yellowlist[i])}])."
            elif symbol == "!":
                if letter not in self.greenlist: self.greenlist.append(letter)
                match[i] = letter
            else:
                if letter not in self.blacklist: self.blacklist.append(letter)
        if self.blacklist:
            self.regex = lookahead + f"(?!\w*[{''.join(self.blacklist)}])" + "".join(match)
        else:
            self.regex = lookahead + "".join(match)
        #print(self.regex)
        self.__update_words_list()
        self.__grade_words()

    def __grade_words(self):
        for word in self.words.keys():
            overall_sum = 0
            chars = list(word)
            for i in range(5):
                overall_sum += self.frequency_list[i][chars[i]]
            self.words[word] = overall_sum

        guess_frequency_list = dict()
        for word in self.words.keys():
            chars = list(word)
            for i in range(5):
                guess_frequency_list[chars[i]] = guess_frequency_list.get(chars[i], 0) + 1
                
        for word in self.guesses.keys():
            overall_sum = 0
            alphabet = dict()
            chars = list(word)
            for i in range(5):
                if chars[i] not in alphabet and chars[i] not in self.greenlist and chars[i] not in self.blacklist and chars[i] not in self.yellowlist[i] and chars[i] in guess_frequency_list:
                    overall_sum += guess_frequency_list[chars[i]]
                    alphabet[chars[i]] = True     
            self.guesses[word] = overall_sum
        
        ### pattern matching
        
    def get_stats(self, listnum: int = 10, verbose=False, engine=False):
        overall_sorted = sorted(self.words.items(),
                                key=lambda k: k[1],
                                reverse=True)
        guess_sorted = sorted(self.guesses.items(),
                                key=lambda k: k[1],
                                reverse=True)
        
        if engine: #[num possible words, top possible word, num sorted guesses, optimal guess]
            return [len(overall_sorted), overall_sorted[0][0], len(guess_sorted), guess_sorted[0][0]]

        retstring = ""
        count = listnum if len(overall_sorted) >= listnum else len(overall_sorted)
        retstring += "Most Likely Word\n"
        if count <= 0:
            retstring += "No Words Likely: Word probably not in current dictionary\n"
        else:
            for i in range(count):
                if verbose:
                    retstring += f"{i + 1}. {overall_sorted[i][0]} - score: {overall_sorted[i][1]}\n"
                else:
                    retstring += f"{i + 1}. {overall_sorted[i][0]}\n"
        
        retstring += "\n"
        
        count = listnum if len(guess_sorted) >= listnum else len(guess_sorted)
        retstring += "Optimal Guesses\n"
        if count <= 0:
            retstring += "No Guesses Left!\n"
        else:
            for i in range(count):
                if verbose:
                    retstring += f"{i + 1}. {guess_sorted[i][0]} - score: {guess_sorted[i][1]}\n"
                else:
                    retstring += f"{i + 1}. {guess_sorted[i][0]}\n"
        return retstring

class WordleHelper():
    
    wordle : Wordle
    
    def __init__(self):
        self.wordle = Wordle("words.txt")
    
    def run(self):
        while(True):
            guess = input("\nEnter guess: \n").lower().strip()
            if guess == "quit":
                return
            result = input("\nEnter result:\n").lower().strip()
            if result == "quit":
                return
            if result == "!!!!!":
                return
            else:
                self.wordle.update(guess, result)
                print(self.wordle.get_stats(20, True))
            
    def debug(self):
        self.wordle.update("arose", "....?")
        print(self.wordle.get_stats(20, True))
        
class WordleEngine():
    
    wordle : Wordle
    txt : str
    words: list
    solution: str = None
    
    def __init__(self, txt : str = "words.txt"):
        self.txt = txt
        with open(self.txt, "r") as words:
            self.words = [line.strip() for line in words]
        self.dataset : dict = {
            "solution" : [],
            "guess_1" : [],
            "result_1" : [],
            "guess_2" : [],
            "result_2" : [],
            "guess_3" : [],
            "result_3" : [],
            "guess_4" : [],
            "result_4" : [],
            "guess_5" : [],
            "result_5" : [],
            "guess_6" : [],
            "result_6" : [],
            "attempts" : [],
        }
            
    def reset(self, solution : str):
        if solution:
            self.solution = solution
        else:
            self.solution = random.choice(self.words)
        self.wordle = Wordle(self.txt)
    
    def grade(self, guess : str) -> str:
        guess_char = list(guess)
        solution_char = list(self.solution)
        
        retstring = ""
        for i in range(5):
            if guess_char[i] == solution_char[i]:
                retstring += "!"
            elif guess_char[i] in self.solution:
                retstring += "?"
            else:
                retstring += "."
        
        return retstring 
    
    def populate_dataset(self, guesses, results, attempts):
        self.dataset["solution"].append(self.solution)
        self.dataset["attempts"].append(attempts)
        for i in range(6):
            try:
                self.dataset["guess_" + str(i+1)].append(guesses[i])
            except IndexError:
                self.dataset["guess_" + str(i+1)].append("N/A")
                
            try:
                self.dataset["result_" + str(i+1)].append(results[i])
            except:
                self.dataset["result_" + str(i+1)].append("N/A")

    def run(self, iterations : int = 10, starting_word : str = None, solution: str = None):
        for i in range(iterations):
            self.reset(solution)
            finished = False
            tries = 0
            data = {"guesses": [], "results": []}
            if not starting_word:
                guess = random.choice(self.words)
            else:
                guess = starting_word
            while(tries < 6):
                tries += 1
                result = self.grade(guess)
                data["guesses"].append(guess)
                data["results"].append(result)
                if result == "!!!!!": # match
                    finished = True
                    break
                self.wordle.update(guess, result)
                options = self.wordle.get_stats(1, False, True)
                guess = options[1] if options[0] < 5 else options[3]
            if finished:
                self.populate_dataset(data["guesses"], data["results"], tries)
            else:
                self.populate_dataset(data["guesses"], data["results"], -1)
        
    def stats(self) -> pandas.DataFrame:
        return pandas.DataFrame(self.dataset)

class WordleExperiments:
    
    words : list
    
    def __init__(self, txt : str = "words.txt"):
        with open(txt, "r") as words:
            self.words = [line.strip() for line in words]
        
    def best_starting_word(self, iterations : int = 100, file : str = "best_starting_words.txt"):
        results = list()
        count = 1
        length = len(self.words)
        for word in self.words:
            try:
                engine = WordleEngine()
                engine.run(iterations, starting_word=word, solution=None)
                df = engine.stats()
                average_tries = df[df["attempts"] != -1]["attempts"].mean()
                wins = df[df["attempts"] != -1]["attempts"].size
                losses = df[df["attempts"] == -1]["attempts"].size
                results.append({"avg_tries": average_tries, "wins": wins, "losses": losses, "word": word})
                print(f"\033[;32m{word}\033[0m - ({count}/{length})")
            except:
                print(f"\033[;32m{word}\033[0m \033[1;31m - Error\033[0m")
                print(engine.solution)
                results.append({"avg_tries": -1, "wins": -1, "losses": -1, "word": word})
            count += 1
            
        with open(file, "w") as txt:
            for result in sorted(results, key = lambda k : k["avg_tries"]):
                string = f"{result['word']} | avg_tries: {result['avg_tries']} | wl_ratio : {result['wins']}/{result['losses']}\n"
                txt.write(string)
            
        
if __name__ == "__main__":
    helper = WordleHelper()
    helper.run()
    
    #WordleExperiments().best_starting_word()
    
    # engine = WordleEngine()
    # engine.run(100)
    # df = engine.stats()
    # average_tries = df[df["attempts"] != -1]["attempts"].mean()
    # wins = df[df["attempts"] != -1]["attempts"].size
    # losses = df[df["attempts"] == -1]["attempts"].size
    # print(f"avg_tries: {average_tries}, wins: {wins}, losses: {losses}")
    # print(df)


# TODO: spreadsheet of worst and best words for solution and starting
# TODO: optimal guess --> 4 happening
# TODO: joann pattern matching