class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        i = len(s) - 1
        length = 0
        
        # пропустить пробелы в конце
        while i >= 0 and s[i] == ' ':
            i -= 1
        
        # считать длину последнего слова
        while i >= 0 and s[i] != ' ':
            length += 1
            i -= 1
        
        return length
