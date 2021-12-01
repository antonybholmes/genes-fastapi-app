lass Stack(object):

    def __init__(self):
        self.__stack = []

    def push(self, v):
        self.__stack.insert(0, v)

    # Use peek to look at the top of the stack
    def peek(self):     
	    return self.__stack[0]
        
    def pop(self):
        return self.__stack.pop()
        
    def tolist(self):
        return self.__stack

    def __iter__(self):
        return self.__stack.__iter__()
        
    def __len__(self):
        return len(self.__stack)
        
    
